"""
CLI from ..validators import ComplianceValidator
from ..schemas import MetaYamlSchema
from ..utils import YamlParser
from ..automation import CIPAutomation, DirectoryMetadataGenerator, GitHubWorkflowGenerator
from ..navigation import RepositoryResolver, DependencyGraph, CrossRepoValidator
from ..vm import CIPVMService, GitHubVMIntegration, load_vm_config point for CIP-Core tools.
"""

import click
from pathlib import Path
import sys
import json

from ..validators import ComplianceValidator
from ..schemas import MetaYamlSchema
from ..utils import YamlParser
from ..automation import CIPAutomation, DirectoryMetadataGenerator, AIEnhancedDirectoryMetadataGenerator, GitHubWorkflowGenerator
from ..navigation import RepositoryResolver, DependencyGraph, ContentDiscovery
from ..instructions import generate_cip_instructions, CIPInstructionsGenerator


@click.group()
@click.version_option(version="0.1.0-dev")
def cli():
    """
    CIP-Core: Cognition Index Protocol Tools
    
    Validate, score, and navigate repositories following the 
    Cognition Index Protocol specification.
    """
    pass


@cli.command()
@click.option("--path", "-p", default=".", help="Path to repository to validate")
@click.option("--format", "-f", default="text", type=click.Choice(["text", "json"]), 
              help="Output format")
@click.option("--config", "-c", help="Path to validation configuration file")
def validate(path: str, format: str, config: str):
    """Validate repository for CIP compliance."""
    
    # Load configuration if provided
    validator_config = {}
    if config:
        try:
            with open(config, 'r') as f:
                validator_config = json.load(f)
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            sys.exit(1)
    
    # Run validation
    validator = ComplianceValidator(validator_config)
    report = validator.validate_repository(path)
    
    # Output results
    if format == "json":
        result = {
            "score": report.score,
            "is_compliant": report.is_compliant,
            "total_checks": report.total_checks,
            "passed_checks": report.passed_checks,
            "issues": [
                {
                    "level": issue.level,
                    "category": issue.category,
                    "message": issue.message,
                    "file_path": issue.file_path,
                    "suggested_fix": issue.suggested_fix
                }
                for issue in report.issues
            ]
        }
        click.echo(json.dumps(result, indent=2))
    else:
        summary = validator.generate_compliance_summary(report)
        click.echo(summary)
    
    # Exit with error code if not compliant
    if not report.is_compliant:
        sys.exit(1)


@cli.command()
@click.option("--type", "-t", default="theory", 
              type=click.Choice(["theory", "sdk", "devkit", "models", "protocol", "infrastructure"]),
              help="Type of repository to initialize")
@click.option("--title", help="Repository title")
@click.option("--description", help="Repository description") 
@click.option("--license", help="Repository license")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing meta.yaml")
def init(type: str, title: str, description: str, license: str, force: bool):
    """Initialize repository with CIP metadata."""
    
    cip_dir = Path(".cip")
    meta_path = cip_dir / "meta.yaml"
    
    # Check if already exists
    if meta_path.exists() and not force:
        click.echo("CIP metadata already exists. Use --force to overwrite.", err=True)
        sys.exit(1)
    
    # Create .cip directory
    cip_dir.mkdir(exist_ok=True)
    
    # Generate meta.yaml template
    schema = MetaYamlSchema()
    template_data = schema.generate_template(
        repository_role=type,
        title=title,
        description=description, 
        license=license
    )
    
    # Write meta.yaml
    import yaml
    with open(meta_path, 'w') as f:
        yaml.dump(template_data, f, default_flow_style=False, sort_keys=False)
    
    click.echo(f"✅ Initialized CIP metadata in {meta_path}")
    click.echo(f"Repository type: {type}")
    click.echo("Run 'cip validate' to check compliance.")


@cli.command()
@click.option("--system", "-s", help="AI system to benchmark")
@click.option("--questions", "-q", default="auto", help="Question set to use")
@click.option("--output", "-o", help="Output file for results")
def score(system: str, questions: str, output: str):
    """Run comprehension scoring benchmark."""
    click.echo("🚧 Comprehension scoring not yet implemented")
    click.echo("This will be available in the next development phase.")


@cli.command()
@click.argument("repo_url")
def resolve(repo_url: str):
    """Resolve repo:// URL to actual content."""
    click.echo("🚧 Repository resolution not yet implemented")
    click.echo(f"Would resolve: {repo_url}")


@cli.command("generate-instructions")
@click.option("--path", "-p", default=".", help="Path to repository root")
@click.option("--validate", is_flag=True, help="Validate generated instructions")
def generate_instructions(path: str, validate: bool):
    """Generate AI instruction files for repository navigation."""
    try:
        click.echo("🤖 Generating CIP instruction files...")
        
        # Generate instructions
        generated_files = generate_cip_instructions(path)
        
        click.echo("✅ Generated instruction files:")
        for instruction_type, file_path in generated_files.items():
            click.echo(f"   📋 {instruction_type}: {file_path}")
        
        # Validate if requested
        if validate:
            click.echo("\n🔍 Validating generated instructions...")
            generator = CIPInstructionsGenerator(path)
            validation = generator.validate_instructions()
            
            if validation["valid"]:
                click.echo("✅ All instruction files valid")
            else:
                click.echo("❌ Validation issues found:")
                for issue in validation["issues"]:
                    click.echo(f"   ⚠️  {issue}")
        
        click.echo("\n🎯 Instructions ready for AI agent consumption!")
        
    except Exception as e:
        click.echo(f"❌ Error generating instructions: {str(e)}", err=True)
        sys.exit(1)


@cli.command("generate-metadata")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing meta.yaml files")
@click.option("--path", "-p", default=".", help="Path to repository root")
def generate_metadata(force: bool, path: str):
    """Generate directory-level meta.yaml files automatically."""
    generator = DirectoryMetadataGenerator(path)
    generator.process_repository(force=force)
    click.echo("✅ Directory metadata generation complete")


@cli.command("install-workflows")
@click.option("--path", "-p", default=".", help="Path to repository root")
def install_workflows(path: str):
    """Install GitHub Actions workflows for CIP automation."""
    generator = GitHubWorkflowGenerator(path)
    generator.install_workflows()
    click.echo("✅ GitHub workflows installed")


@cli.command("bootstrap")
@click.option("--type", "-t", default="theory",
              type=click.Choice(["theory", "sdk", "devkit", "models", "protocol", "infrastructure"]),
              help="Type of repository to bootstrap")
@click.option("--path", "-p", default=".", help="Path to repository root")
def bootstrap(type: str, path: str):
    """Bootstrap complete CIP automation for a repository."""
    automation = CIPAutomation(path)
    report = automation.bootstrap_repository(type)
    
    click.echo(f"\n🎉 Repository bootstrapped successfully!")
    click.echo(f"Compliance Score: {report.score:.1%}")
    
    if not report.is_compliant:
        click.echo("\n⚠️  Some issues need attention:")
        for issue in report.issues:
            if issue.level == "error":
                click.echo(f"❌ {issue.message}")


@cli.command("resolve")
@click.argument("repo_url")
@click.option("--ecosystem-root", "-e", help="Root directory containing repositories")
@click.option("--format", "-f", default="text", type=click.Choice(["text", "json"]))
def resolve(repo_url: str, ecosystem_root: str, format: str):
    """Resolve repo:// URL to actual content."""
    resolver = RepositoryResolver(ecosystem_root)
    result = resolver.resolve_content(repo_url)
    
    if format == "json":
        import json
        output = {
            "url": repo_url,
            "exists": result.exists,
            "content_type": result.content_type,
            "repository_path": result.repository_path,
            "content_path": result.content_path,
            "metadata": result.metadata
        }
        click.echo(json.dumps(output, indent=2))
    else:
        if result.exists:
            click.echo(f"✅ Resolved: {repo_url}")
            click.echo(f"Repository: {result.repository_path}")
            click.echo(f"Content: {result.content_path}")
            click.echo(f"Type: {result.content_type}")
        else:
            click.echo(f"❌ Not found: {repo_url}")
            if result.metadata and 'error' in result.metadata:
                click.echo(f"Error: {result.metadata['error']}")


@cli.command("list-repos")
@click.option("--ecosystem-root", "-e", help="Root directory containing repositories")
@click.option("--format", "-f", default="text", type=click.Choice(["text", "json"]))
def list_repos(ecosystem_root: str, format: str):
    """List all repositories in the ecosystem."""
    resolver = RepositoryResolver(ecosystem_root)
    repositories = resolver.list_repositories()
    
    if format == "json":
        import json
        click.echo(json.dumps(repositories, indent=2))
    else:
        click.echo("🌌 Dawn Field Theory Ecosystem Repositories")
        click.echo("=" * 50)
        for name, info in repositories.items():
            click.echo(f"\n📦 {name}")
            click.echo(f"   Role: {info['repository_role']}")
            click.echo(f"   Title: {info['title']}")
            click.echo(f"   Version: {info['version']}")
            click.echo(f"   Path: {info['path']}")


@cli.command("validate-links")
@click.option("--repository", "-r", help="Repository name to validate links for")
@click.option("--ecosystem-root", "-e", help="Root directory containing repositories")
@click.option("--format", "-f", default="text", type=click.Choice(["text", "json"]))
def validate_links(repository: str, ecosystem_root: str, format: str):
    """Validate ecosystem links for a repository."""
    resolver = RepositoryResolver(ecosystem_root)
    
    if repository:
        repos_to_check = [repository]
    else:
        repos_to_check = list(resolver.list_repositories().keys())
    
    all_results = {}
    
    for repo in repos_to_check:
        results = resolver.validate_ecosystem_links(repo)
        all_results[repo] = results
    
    if format == "json":
        import json
        click.echo(json.dumps(all_results, indent=2))
    else:
        click.echo("🔗 Ecosystem Link Validation")
        click.echo("=" * 30)
        
        for repo, results in all_results.items():
            click.echo(f"\n📦 {repo}")
            if not results or (len(results) == 1 and 'error' in results[0]):
                click.echo("   ❌ Repository not found or no links")
                continue
            
            for result in results:
                if 'error' in result:
                    continue
                
                status = "✅" if result['exists'] else "❌"
                click.echo(f"   {status} {result['link_name']}: {result['url']}")
                if not result['exists'] and result['error']:
                    click.echo(f"      Error: {result['error']}")


# VM Service Commands
@cli.group("vm")
def vm():
    """CIP VM service commands for AI-powered analysis."""
    pass


@vm.command("trigger")
@click.option("--type", "-t", 
              type=click.Choice(["scrutiny", "metadata-update", "comprehension-benchmark"]),
              default="scrutiny", help="Type of analysis to run")
@click.option("--model", "-m", default="llama3.1", help="Ollama model to use")
@click.option("--repository", "-r", default=".", help="Repository path or repo:// URL")
@click.option("--wait", is_flag=True, help="Wait for job completion")
@click.option("--output", "-o", help="Output file for results")
def vm_trigger(type: str, model: str, repository: str, wait: bool, output: str):
    """Trigger analysis job on CIP VM service."""
    try:
        config = load_vm_config()
        vm_service = CIPVMService(config)
        
        click.echo(f"🚀 Triggering {type} analysis on VM...")
        
        # Trigger appropriate job type
        if type == "scrutiny":
            job = vm_service.trigger_scrutiny_analysis(repository, model)
        elif type == "metadata-update":
            job = vm_service.trigger_metadata_update(repository, model)
        elif type == "comprehension-benchmark":
            job = vm_service.trigger_comprehension_benchmark(repository)
        
        click.echo(f"✅ Job {job.job_id} started")
        
        if wait:
            click.echo("⏳ Waiting for completion...")
            job = vm_service.wait_for_completion(job.job_id)
            
            if job.status == "completed":
                click.echo("✅ Analysis completed!")
                if output and job.results:
                    with open(output, 'w') as f:
                        json.dump(job.results, f, indent=2)
                    click.echo(f"📄 Results saved to {output}")
                elif job.results:
                    click.echo("📊 Results:")
                    click.echo(json.dumps(job.results, indent=2))
            else:
                click.echo(f"❌ Job failed: {job.error_message}")
                sys.exit(1)
        else:
            click.echo(f"Use 'cip vm status {job.job_id}' to check progress")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@vm.command("status")
@click.argument("job_id", required=False)
def vm_status(job_id: str):
    """Check VM service or job status."""
    try:
        config = load_vm_config()
        vm_service = CIPVMService(config)
        
        if job_id:
            job = vm_service.get_job_status(job_id)
            click.echo(f"Job {job_id}: {job.status}")
            if job.status == "completed" and job.results:
                click.echo("📊 Results available")
            elif job.status == "failed":
                click.echo(f"❌ Error: {job.error_message}")
        else:
            status = vm_service.get_vm_status()
            click.echo("🖥️  VM Service Status:")
            click.echo(json.dumps(status, indent=2))
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@vm.command("models")
def vm_models():
    """List available Ollama models on VM."""
    try:
        config = load_vm_config()
        vm_service = CIPVMService(config)
        
        models = vm_service.list_available_models()
        click.echo("🤖 Available Ollama Models:")
        for model in models:
            click.echo(f"  - {model}")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("ai-enhance")
@click.option("--model", "-m", default="codellama:latest", help="Ollama model to use")
@click.option("--path", "-p", default=".", help="Repository path")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing meta.yaml files")
@click.option("--test-only", is_flag=True, help="Test on one directory only")
def ai_enhance(model: str, path: str, force: bool, test_only: bool):
    """AI-enhanced metadata generation using local Ollama."""
    try:
        from ..ollama_local import AIMetadataEnhancer, test_ollama_integration
        
        if test_only:
            click.echo(f"🧪 Testing AI enhancement with {model}")
            result = test_ollama_integration(path, model)
            if result:
                click.echo("✅ AI enhancement test successful!")
            return
        
        # Full repository processing
        enhancer = AIMetadataEnhancer(model)
        repo_path = Path(path)
        enhancer.process_repository(repo_path, force)
        
        click.echo("✅ AI-enhanced metadata generation complete!")
        
    except ImportError as e:
        click.echo(f"❌ Ollama integration not available: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("ai-metadata")
@click.option("--model", "-m", default="codellama:latest", help="Ollama model to use")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing meta.yaml files")
@click.option("--path", "-p", default=".", help="Path to repository root")
def ai_metadata(model: str, force: bool, path: str):
    """Generate AI-enhanced directory metadata using Ollama."""
    try:
        click.echo(f"🤖 Generating AI-enhanced metadata with {model}...")
        
        generator = AIEnhancedDirectoryMetadataGenerator(path, model)
        generator.process_repository(force=force)
        
        click.echo("✅ AI-enhanced metadata generation complete!")
        click.echo("🎯 Run 'cip generate-instructions' to create AI guidance files!")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("generate-metadata")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing meta.yaml files")
@click.option("--path", "-p", default=".", help="Path to repository root")
def generate_metadata(force: bool, path: str):
    """Generate directory-level meta.yaml files automatically (rule-based)."""
    generator = DirectoryMetadataGenerator(path)
    generator.process_repository(force=force)
    click.echo("✅ Directory metadata generation complete")


@vm.command("install-workflow")
@click.option("--path", "-p", default=".", help="Repository path")
@click.option("--name", "-n", default="cip-vm-analysis", help="Workflow name")
def vm_install_workflow(path: str, name: str):
    """Install GitHub workflow for VM analysis."""
    from ..vm import GitHubVMIntegration
    integration = GitHubVMIntegration()
    integration.install_vm_workflow(path, name)
    click.echo("✅ VM workflow installed")
    click.echo("⚙️  Don't forget to set secrets:")
    click.echo("   - CIP_VM_ENDPOINT")
    click.echo("   - CIP_VM_API_KEY")


if __name__ == "__main__":
    cli()
