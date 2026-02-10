Here's a comprehensive guideline for future commits made by me and eventually anyone who would like to partecipate in the project.

## Changes
1. Make small and resonable changes. It's very dirty making large changes, especially if they are not directly related one to another.
2. Use `git rebase --interactive` on your branches before pushing to slice your changes into smaller pieces.
3. **DO NOT USE AI TO GENERATE ANY CODE!!!** Autocompletions are fine.
4. Document the changes to the API or else find yourself in debuging something you have no clue about.
5. Write tests for new features.
5. Run tests before pushing anything that is not docs, ci or chore related.

## Git
Use conventional commits notation.

The project uses the following prefixes:
- feat - for new features that didn't exist before the commit
- refactor - for any refactor of already existing features in the codebase
- fix - for non urgent fixes
- hotfix - for urgent fixes
- ci - for everything that is related to the ci/cd pipeline
- docs - for any documentation changes
- chore - for anything that doesn't affect the code execution (comments, version bumps, displayed text)
- test - for anything that is related to the test cases

In addition, most of the commits must specify the area they affect:
- repo - for anything that is specific to the backend repos
- usecase - for anything that is specific to the backend usecases
- service - for anything that is specific to the backend services
- db - for anything that is specific to the database
- telegram - for anything that is specific to code in telegram bot codebase

All other conventional commits rules are applied too.

## Chore
1. Stick to the Object-Oriented Programming.
2. Beware of the SOLID and DRY principles.