---
applyTo: '**'
---
# Zenodo Workflow Instructions

> Load this module when uploading papers to Zenodo or managing DOIs.

## DOI Registry

The canonical source of truth for all publications is:
```
citations/doi_registry.yaml
```

### Registry Structure
```yaml
schema_version: "1.0"
last_updated: "YYYY-MM-DD"

published:
  - id: paper_snake_case_id
    title: "Full Paper Title"
    short_title: "Short Title"
    doi: "10.5281/zenodo.XXXXXXXX"
    zenodo_record: XXXXXXXX
    url: "https://zenodo.org/records/XXXXXXXX"
    version: "1.0"
    upload_date: "YYYY-MM-DD"
    category: core_theory|validation|theoretical|implementation|mathematical
    status: published
    has_code: true|false
    has_data: true|false
    has_figures: true|false
    # For version updates:
    previous_version:
      doi: "10.5281/zenodo.XXXXXXXX"
      version: "1.0"
```

## Upload Workflow

### New Paper Upload

1. **Package location**: `foundational/docs/preprints/zenodo_packages/`
2. **Upload URL**: https://zenodo.org/uploads/new
3. **Form fields**:

| Field | Standard Value |
|-------|----------------|
| Resource type | Publication → Preprint |
| License | GNU Affero General Public License v3.0 |
| Creators | Author Name · ORCID: XXXX-XXXX-XXXX-XXXX · Affiliation |

4. **After upload**: Update `doi_registry.yaml` with new DOI

### Version Update Upload

1. Go to existing Zenodo record URL
2. Click "New version"
3. Upload new package
4. Update version number in form
5. Update `doi_registry.yaml`:
   - Change `doi`, `zenodo_record`, `url` to new values
   - Update `version` (e.g., "1.0" → "2.0")
   - Add `previous_version` block
   - Update `upload_date`

## Description Template

Use this structure for comprehensive descriptions:

```markdown
> Brief 1-2 sentence summary of the paper's main contribution.
>
> **Key Findings:**
> - Finding 1 with specific metric (e.g., p < 0.001)
> - Finding 2 with quantified result
> - Finding 3 with validation details
>
> **Theoretical Framework:**
> 2-3 sentences explaining the conceptual basis and how this fits
> into the broader research program.
>
> **Validation Approach:**
> 2-3 sentences on methodology, what was tested, significance levels.
>
> **Package Contains:**
> - Complete paper (PDF + Markdown)
> - Code/ - All simulation and analysis scripts
> - Data/ - Raw experimental outputs (JSON)
> - Figures/ - Publication-quality figures with generation scripts
> - README with reproduction instructions
>
> [Optional: Statement about reproducibility or falsification approach]
```

## Keywords Template

Include 8-12 keywords:
- 2-3 primary concepts from paper
- 2-3 methodological terms
- 2-3 framework terms (PAC, SEC, etc.)
- 1-2 domain terms
- "Dawn Field Theory" (always include)

Example:
```
Cellular automata, Rule 110, Edge of chaos, Golden ratio, φ-clustering,
Xi constant, Emergence dynamics, Information theory, Dawn Field Theory
```

## Related Works

Use Zenodo's "Related works" feature:
- `is supplemented by this upload` - for papers this one supports
- `supplements` - for papers that support this one
- Format: `10.5281/zenodo.XXXXXXXX`

## After All Uploads

1. **Commit registry**: `git add citations/doi_registry.yaml`
2. **Create tag**: `git tag -a vX.Y.Z -m "Release message"`
3. **Push with tags**: `git push origin main --tags`
4. **Create GitHub release** from tag

## Package Naming Convention

```
{paper_id}_v{version}_{YYYYMMDD}_{HHMMSS}.zip
```

Example: `cellular_automata_xi_clustering_v1.0_20251228_103345.zip`

## Package Contents Standard

Every package must include:
```
package_name/
├── Paper.pdf           # Formatted paper
├── Paper.md            # Source markdown
├── README.md           # Reproduction instructions
├── Code/
│   └── *.py            # All scripts
├── Data/
│   └── *.json          # Raw outputs
└── Figures/
    └── *.png           # Publication figures
```
