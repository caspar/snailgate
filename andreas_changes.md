# This Document sums up Andreas' changes

# Changes

- Restructured the repository. When I started working on it it was only possible for 1 person to work on it locally, now it allows reproducible results and enables collaboration between different contributors.
- Upgraded deprecated packages that were affecting the way the application was functioning, especially for the differential equations solver.
- Fixed the package dependencies for reproducibility.
- Connected the frontend to the backend. Initially, the repo was using both Flask and Tornado and neither of them was connected to the frontend client resulting in the graphics and simulation animations not working.
- Dockerized the application. It creates two containers one for the frontend (snailgate-client) and one for the client (snailgate-server) and pushes the images to the docker hub, meaning that instead of building the application from the source, you can pull and run the docker container without any other dependencies or packages installed.
