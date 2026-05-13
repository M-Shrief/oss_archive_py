# OSS Archive


- [Objectives](#objectives)
- [Setup](#setup)


## Objectives and Goals
This Project aims to archive and save Open-Source Software projects from multiple sources (github,codeberg,gitlab...etc), and distribute them. Therefor, it'll save this projects from being locked in and controlled by Nations and Organizations.

This project's core objective is to achieve **Strategic Autonomy**, and not to be under the authority of other nations or even organizations, which can undermine our ability to achieve our strategic goals.

This project aim to build an archive/mirror for Open-Source Software projects, and preventing any attempt to lock poeple's access. It doesn't aim to be a Version Control System (VCS) like github or codeberg which is used for active development with DevOps features, it's just an archive/mirror.

Nevertheless, It can be a part of a bigger system, that uses this project as a component, and then it can provide **Version Control System (VCS)** service - like github - for programmers and users.

This project will use any tool that can facilitate and ease the way people can archive open-source software, and to be able share and save this archive/mirror. We can use traditional ways like cloning the OSS's repo, and the use non-traditional ways - in the software industry -  by using Torrent to distribute this archive/mirror. In other words, no method or tool is excluded, anything that facilitates the goal is used.

There's multiple projects in the world to achive the core objective of this project, like:
- [Gitee](https://gitee.com/) in China
    > Gitee was chosen by the Ministry of Industry and Information Technology of the Chinese government to make an "independent, open-sourcecode hosting platform for China." [source](https://techcrunch.com/2020/08/21/china-is-building-its-github-alternative-gitee/)

- [AtomicGit | GitCode](https://gitcode.com/) 
    > AtomicGit | GitCode is a next-generation, AI-driven open-source code hosting platform launched in September 2023 by CSDN and Huawei Cloud CodeArts, operated by Chongqing Open Source Co-creation Technology Co., Ltd. It serves as a comprehensive developer service ecosystem that integrates code hosting, collaborative R&D, project management, and open-source operation support for individual developers, teams, and enterprises. 


- [Codeberg](https://codeberg.org/) in Europe
    > The organization selected the European Union for their headquarters and computer infrastructure, due to members' concerns that a software project repository hosted in the United States could be removed if a malicious actor made bad faith copyright claims under the [Digital Millennium Copyright Act](https://en.wikipedia.org/wiki/Digital_Millennium_Copyright_Act).


This Project will attempt to archive multiple Open-Source Software from different categories, like:
- Operating Systems (Arch, Gentoo,...etc)
- Databases (like PostgreSQL, Redis, SQLite,...etc)
- Programming Languages and Compilers (like C, Go, Zig,...etc)
- Programming Frameworks:
    - Web (like Vite.js, Vuejs)
    - Gaming Development (Godot)
- Development Tools and DX:
    - IDEs (like Vim, Zed, VSCodium,...etc)
    - Language Servers
    - Linters
    - other extenstions.
- Virtual Machines and Containerization (Docker, LXC, Podman,...etc)
- **PKMS**: Personal Knowledge Managment Systems  (like SiYuan)
- Graphics and 3D (like Blender)
- Version Control Systems (like Forgejo, Gitea...etc)

## Setup

- Setup your virtual environment:
```sh
$ python -m venv .venv
```

- use the virtual environment with poetry
```sh
$ poetry env use .venv/bin/python3
```

- Install project packages:
```sh
$ poetry install 
```

- Run the app:
```sh
$ poetry run uvicorn oss_archive.main:app --reload
```
