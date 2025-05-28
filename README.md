
## Development Guidelines
1. **Test Organization**:
   - Create separate folders for each major test case
   - Include a `README.md` in each folder explaining its purpose

2. **Version Control**:
   - Never commit library folders (add to `.gitignore`)
   - Document required libraries in `dependencies.txt`
   - Keep test assets in appropriate `/experiments/` subfolders

3. **Testing Protocol**:
   - Maintain test logs in `/test-results/`
   - Clearly label experimental vs production-ready code
   - Document API endpoints and data formats

## Important Notes
⚠️ This is an experimental branch - code may be unstable  
⚠️ Library dependencies must be documented, not committed  
⚠️ Merge to main only after thorough testing and review
