# Authentication + Authorization process
Right now, just for demonstration purposes, I'm realying on a path variable to identify the user, but this is totally NOT prod ready. If this project will go live, it is really needed to use something to authenticate users. It could be a 3rd party auth just as (Sign with Google, for example)

# Expose swagger on prod. env.
The swagger must be not available for the client. Again, this is just because is not a PROD. ready app.

# MVC -> Clean Arch
Since the number of features are really low, it was not needed to create a complex. design pattern fully reusable. But if this system grows, it definetly would be better some more robust system with SOLID principles.

# Database Connection Pools
I did not perform any study about the database/api capacity in heavy workload scenario. In real projects, it is needed to understand how many simuteniously connections each API and DB replica are able to handle.

# Branch strategy, CI/CD
Since I was the only one developing, I commit everything direclty to main, but this is something that when I am working in a team, something very "avoidable". I really enjoy doing [Gitflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) or [Github Flow](https://docs.github.com/en/get-started/using-github/github-flow), but in that case will be only 