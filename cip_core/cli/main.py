"""
CLI entry point for CIP-Core tools.
"""

import click
from pathlib import Path
import sys
import json

# New unified imports
from ..engine import CIPEngine
from ..engine.core import InitConfig
from ..engine.repository import ProjectType
from ..engine.config import GenerationConfig

# Legacy imports for backwards compatibility where needed
from ..schemas import MetaYamlSchema
from ..utils import YamlParser
from ..automation import GitHubWorkflowGenerator
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
    
    try:
        # Initialize CIP engine
        engine = CIPEngine(repo_path=path)
        
        # Load custom validation configuration if provided
        if config:
            try:
                with open(config, 'r') as f:
                    config_data = json.load(f)
                # Apply custom config to engine if needed
                engine.update_config(config_data)
            except Exception as e:
                click.echo(f"Error loading config: {e}", err=True)
                sys.exit(1)
        
        # Run validation using unified engine
        result = engine.validate_repository()
        
        # Convert ValidationResult to ComplianceReport format for output consistency
        if format == "json":
            output = {
                "score": result.score,
                "is_compliant": result.score >= 0.8,  # Use same threshold as ComplianceValidator
                "total_checks": result.total_checks,
                "passed_checks": result.passed_checks,
                "issues": result.issues
            }
            click.echo(json.dumps(output, indent=2))
        else:
            # Generate text summary similar to original format
            click.echo("CIP Compliance Report")
            click.echo("====================")
            click.echo()
            click.echo(f"Repository: {path}")
            
            if result.score >= 0.8:
                status = "✅ COMPLIANT"
            else:
                status = "❌ NON-COMPLIANT"
            
            click.echo(f"Status: {status}")
            click.echo(f"Score: {result.score:.1%} ({result.passed_checks}/{result.total_checks} checks passed)")
            
            if result.issues:
                click.echo()
                click.echo("Issues Found:")
                
                # Group issues by level
                errors = [i for i in result.issues if i['level'] == 'error']
                warnings = [i for i in result.issues if i['level'] == 'warning']
                
                for issue in errors:
                    click.echo(f"❌ {issue['category'].upper()}: {issue['message']}")
                    if issue.get('suggested_fix'):
                        click.echo(f"   💡 {issue['suggested_fix']}")
                
                for issue in warnings:
                    click.echo(f"⚠️ {issue['category'].upper()}: {issue['message']}")
                    if issue.get('suggested_fix'):
                        click.echo(f"   💡 {issue['suggested_fix']}")
        
        # Exit with error code if not compliant
        if result.score < 0.8:
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Validation failed: {str(e)}", err=True)
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
    
    try:
        # Map CLI type to ProjectType enum
        type_mapping = {
            "theory": ProjectType.THEORY,
            "sdk": ProjectType.SDK, 
            "devkit": ProjectType.DEVKIT,
            "models": ProjectType.MODELS,
            "protocol": ProjectType.PROTOCOL,
            "infrastructure": ProjectType.INFRASTRUCTURE
        }
        
        project_type = type_mapping.get(type, ProjectType.THEORY)
        
        # Create initialization config
        init_config = InitConfig(
            project_type=project_type,
            title=title,
            description=description,
            license=license,
            force=force
        )
        
        # Initialize with CIP engine
        engine = CIPEngine(repo_path=".")
        result = engine.initialize_repository(init_config)
        
        click.echo(f"✅ Initialized CIP metadata")
        click.echo(f"Repository type: {type}")
        click.echo("Run 'cip validate' to check compliance.")
        
    except Exception as e:
        click.echo(f"Initialization failed: {str(e)}", err=True)
        sys.exit(1)


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
        
        # Initialize CIP engine
        engine = CIPEngine(repo_path=path)
        
        # Generate instructions using unified engine
        result = engine.generate_instructions()
        
        if result.success:
            click.echo("✅ Generated instruction files:")
            # Parse the content to show generated files
            lines = result.content.split('\n')
            for line in lines:
                if line.startswith('- '):
                    click.echo(f"   📋 {line[2:]}")
        else:
            click.echo(f"❌ Instruction generation failed: {', '.join(result.errors)}")
            sys.exit(1)
        
        # Validate if requested
        if validate:
            click.echo("\n🔍 Validating generated instructions...")
            validation = engine.instructions.validate_instructions()
            
            if validation.get("valid", False):
                click.echo("✅ All instruction files valid")
            else:
                click.echo("❌ Validation issues found:")
                for issue in validation.get("errors", []):
                    click.echo(f"   ⚠️  {issue}")
        
        click.echo("\n🎯 Instructions ready for AI agent consumption!")
        
    except Exception as e:
        click.echo(f"❌ Error generating instructions: {str(e)}", err=True)
        sys.exit(1)


@cli.command("generate-metadata")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing meta.yaml files")
@click.option("--path", "-p", default=".", help="Path to repository root")
def generate_metadata(force: bool, path: str):
    """Generate directory-level meta.yaml files automatically (rule-based)."""
    try:
        engine = CIPEngine(repo_path=path)
        config = GenerationConfig(
            strategy="rule_based",
            force_overwrite=force
        )
        result = engine.generate_metadata("rule_based", config)
        
        if result.success:
            click.echo("✅ Directory metadata generation complete")
            if result.files_created:
                click.echo(f"Created {len(result.files_created)} new metadata files")
            if result.files_updated:
                click.echo(f"Updated {len(result.files_updated)} existing metadata files")
        else:
            click.echo(f"❌ Metadata generation failed: {', '.join(result.errors)}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Metadata generation failed: {str(e)}", err=True)
        sys.exit(1)


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
    try:
        # Map CLI type to ProjectType enum
        type_mapping = {
            "theory": ProjectType.THEORY,
            "sdk": ProjectType.SDK,
            "devkit": ProjectType.DEVKIT,
            "models": ProjectType.MODELS,
            "protocol": ProjectType.PROTOCOL,
            "infrastructure": ProjectType.INFRASTRUCTURE
        }
        
        project_type = type_mapping.get(type, ProjectType.THEORY)
        
        # Initialize repository
        engine = CIPEngine(repo_path=path)
        init_config = InitConfig(project_type=project_type)
        init_result = engine.initialize_repository(init_config)
        
        # Generate metadata and instructions
        generation_config = GenerationConfig(strategy="rule_based", force_overwrite=False)
        metadata_result = engine.generate_metadata("rule_based", generation_config)
        
        # Validate the repository
        validation_result = engine.validate_repository()
        
        click.echo(f"\n🎉 Repository bootstrapped successfully!")
        click.echo(f"Compliance Score: {validation_result.score:.1%}")
        
        if not validation_result.is_compliant:
            click.echo("\n⚠️  Some issues need attention:")
            for issue in validation_result.issues[:5]:  # Show first 5 issues
                click.echo(f"❌ {issue}")
                
    except Exception as e:
        click.echo(f"Bootstrap failed: {str(e)}", err=True)
        sys.exit(1)


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
        
        # Initialize CIP engine
        engine = CIPEngine(repo_path=path)
        
        # Configure for AI-enhanced generation
        from ..engine.config import GenerationConfig
        ai_config = GenerationConfig(
            strategy='ai_enhanced',
            ai_model=model,
            force_overwrite=force
        )
        
        # Generate metadata using unified engine
        result = engine.generate_metadata('ai_enhanced', ai_config)
        
        if result.success:
            click.echo("✅ AI-enhanced metadata generation complete!")
            click.echo("🎯 Run 'cip generate-instructions' to create AI guidance files!")
        else:
            click.echo(f"❌ Metadata generation failed: {', '.join(result.errors)}")
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("generate-metadata")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing meta.yaml files")
@click.option("--path", "-p", default=".", help="Path to repository root")
def generate_metadata(force: bool, path: str):
    """Generate directory-level meta.yaml files automatically (rule-based)."""
    try:
        # Initialize CIP engine
        engine = CIPEngine(repo_path=path)
        
        # Configure for rule-based generation
        from ..engine.config import GenerationConfig
        gen_config = GenerationConfig(
            strategy='rule_based',
            force_overwrite=force
        )
        
        # Generate metadata using unified engine
        result = engine.generate_metadata('rule_based', gen_config)
        
        if result.success:
            click.echo("✅ Directory metadata generation complete")
        else:
            click.echo(f"❌ Metadata generation failed: {', '.join(result.errors)}")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


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
