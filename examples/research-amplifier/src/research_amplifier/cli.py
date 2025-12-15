"""
CLI - Command-line interface for Research Amplifier.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="amplify",
    help="Research Amplifier - AI-powered social media for research communication",
)
console = Console()


@app.command()
def init(
    path: Path = typer.Argument(Path("."), help="Repository path"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
):
    """Initialize Research Amplifier in a repository."""
    cip_path = path / "cip"
    
    if cip_path.exists() and not force:
        console.print("[yellow]cip/ directory already exists. Use --force to reinitialize.[/yellow]")
        raise typer.Exit(1)
    
    # Create directory structure
    (cip_path / "concepts").mkdir(parents=True, exist_ok=True)
    (cip_path / "entries").mkdir(parents=True, exist_ok=True)
    
    # Create example knowledge graph
    kg_file = cip_path / "knowledge-graph.yaml"
    if not kg_file.exists() or force:
        kg_content = '''metadata:
  schema_version: "2.0.0"
  project: "my-research"
  description: "Research knowledge graph"
  updated: ""

concepts: {}

relationships: []
'''
        kg_file.write_text(kg_content)
    
    console.print(f"[green]✓ Initialized Research Amplifier in {path}[/green]")
    console.print(f"  Created: {cip_path}/")
    console.print(f"  Created: {cip_path}/concepts/")
    console.print(f"  Created: {cip_path}/entries/")
    console.print(f"  Created: {kg_file}")
    console.print("\n[dim]Next: Add concepts with 'amplify concept add'[/dim]")


@app.command()
def status(
    path: Path = typer.Argument(Path("."), help="Repository path"),
):
    """Show knowledge graph status."""
    from research_amplifier.knowledge import KnowledgeGraph
    
    try:
        kg = KnowledgeGraph.load(path)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[dim]Run 'amplify init' first.[/dim]")
        raise typer.Exit(1)
    
    # Concepts table
    table = Table(title="Knowledge Graph Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Project", kg.metadata.get("project", "unknown"))
    table.add_row("Schema Version", kg.metadata.get("schema_version", "unknown"))
    table.add_row("Concepts", str(len(kg.concepts)))
    table.add_row("Relationships", str(len(kg.relationships)))
    
    entries = kg.get_entries(days=30, unposted_only=False)
    unposted = [e for e in entries if not e.posted]
    table.add_row("Recent Entries (30d)", str(len(entries)))
    table.add_row("Unposted Entries", str(len(unposted)))
    
    console.print(table)
    
    # Validation
    issues = kg.validate()
    if issues:
        console.print(f"\n[yellow]⚠ {len(issues)} validation issues:[/yellow]")
        for issue in issues:
            console.print(f"  - {issue}")
    else:
        console.print("\n[green]✓ Knowledge graph valid[/green]")


@app.command()
def generate(
    entry_id: str = typer.Argument(..., help="Entry ID to generate post for"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Repository path"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Don't create PR"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSON file"),
):
    """Generate social media posts for an entry."""
    from research_amplifier.knowledge import KnowledgeGraph
    from research_amplifier.mitosis import ContextAssembler
    from research_amplifier.agents import AgentPipeline
    
    console.print(f"[dim]Loading knowledge graph from {path}...[/dim]")
    
    try:
        kg = KnowledgeGraph.load(path)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    
    # Assemble context
    console.print(f"[dim]Assembling context for {entry_id}...[/dim]")
    assembler = ContextAssembler(kg)
    
    try:
        context = assembler.assemble(entry_id)
    except KeyError:
        console.print(f"[red]Entry not found: {entry_id}[/red]")
        raise typer.Exit(1)
    
    console.print(f"  Loaded {len(context.concepts)} concepts")
    console.print(f"  Token estimate: ~{context.token_estimate}")
    
    # Run pipeline
    console.print("\n[dim]Running agent pipeline...[/dim]")
    pipeline = AgentPipeline()
    
    if dry_run:
        post = pipeline.run_dry(context)
        result_json = post.__dict__
    else:
        result = pipeline.run(context)
        result_json = result.to_json()
        
        if result.success:
            console.print(f"[green]✓ Post generated successfully ({result.iterations} iterations)[/green]")
        else:
            console.print(f"[yellow]⚠ Post generated with warnings ({result.iterations} iterations)[/yellow]")
    
    # Output
    if output:
        output.write_text(result_json if isinstance(result_json, str) else str(result_json))
        console.print(f"\n[dim]Saved to {output}[/dim]")
    else:
        console.print("\n--- Generated Posts ---\n")
        if dry_run:
            console.print(f"[bold]Twitter:[/bold]\n{post.twitter_content}\n")
            console.print(f"[bold]LinkedIn:[/bold]\n{post.linkedin_content}\n")
        else:
            import json
            data = json.loads(result_json)
            console.print(f"[bold]Twitter:[/bold]\n{data['platforms']['twitter']['content']}\n")
            console.print(f"[bold]LinkedIn:[/bold]\n{data['platforms']['linkedin']['content']}\n")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Repository path"),
    limit: int = typer.Option(5, "--limit", "-l", help="Max results"),
):
    """Search concepts in knowledge graph."""
    from research_amplifier.knowledge import KnowledgeGraph
    
    try:
        kg = KnowledgeGraph.load(path)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    
    results = kg.search(query, limit=limit)
    
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
    
    table = Table(title=f"Search: '{query}'")
    table.add_column("Concept", style="cyan")
    table.add_column("Score", style="green")
    table.add_column("Definition")
    
    for concept_id, score in results:
        concept = kg.get_concept(concept_id)
        definition = concept.definition[:60] + "..." if len(concept.definition) > 60 else concept.definition
        table.add_row(concept_id, f"{score:.2f}", definition)
    
    console.print(table)


@app.command()
def entries(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Repository path"),
    days: int = typer.Option(30, "--days", "-d", help="Days to look back"),
    all: bool = typer.Option(False, "--all", "-a", help="Include posted entries"),
):
    """List recent entries."""
    from research_amplifier.knowledge import KnowledgeGraph
    
    try:
        kg = KnowledgeGraph.load(path)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    
    entries_list = kg.get_entries(days=days, unposted_only=not all)
    
    if not entries_list:
        console.print("[yellow]No entries found.[/yellow]")
        return
    
    table = Table(title=f"Entries (last {days} days)")
    table.add_column("ID", style="cyan")
    table.add_column("Type")
    table.add_column("Significance")
    table.add_column("Posted", style="green")
    table.add_column("One-liner")
    
    for entry in entries_list:
        posted = "✓" if entry.posted else ""
        one_liner = entry.summary.one_liner[:40] + "..." if len(entry.summary.one_liner) > 40 else entry.summary.one_liner
        table.add_row(
            entry.entry_id,
            entry.type,
            entry.significance.level,
            posted,
            one_liner,
        )
    
    console.print(table)


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
