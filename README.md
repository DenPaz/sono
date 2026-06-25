<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/DenPaz/sono">
    <!-- Você pode substituir a URL da imagem abaixo por uma logo real do seu projeto -->
    <img src="https://raw.githubusercontent.com/othneildrew/Best-README-Template/master/images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Sono</h3>

  <p align="center">
    A full-stack Django application with a modern frontend using Vite, Tailwind CSS 4, DaisyUI 5, Alpine.js, and HTMX.
    <br />
    <a href="https://github.com/DenPaz/sono"><strong>Explore a documentação »</strong></a>
    <br />
    <br />
    <a href="https://github.com/DenPaz/sono">Ver Demonstração</a>
    ·
    <a href="https://github.com/DenPaz/sono/issues">Reportar Bug</a>
    ·
    <a href="https://github.com/DenPaz/sono/issues">Solicitar Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Tabela de Conteúdos</summary>
  <ol>
    <li>
      <a href="#sobre-o-projeto">Sobre o Projeto</a>
      <ul>
        <li><a href="#feito-com">Feito com</a></li>
      </ul>
    </li>
    <li><a href="#arquitetura">Arquitetura</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#capturas-de-tela">Capturas de Tela</a></li>
    <li>
      <a href="#começando">Começando</a>
      <ul>
        <li><a href="#pré-requisitos">Pré-requisitos</a></li>
        <li><a href="#instalação">Instalação</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contribuindo">Contribuindo</a></li>
    <li><a href="#licença">Licença</a></li>
    <li><a href="#contato">Contato</a></li>
  </ol>
</details>

## Sobre o Projeto

O Sono é uma aplicação voltada para gerenciamento e acompanhamento de pacientes e dependentes (como em contextos clínicos ou familiares), com três perfis principais: Administradores, Especialistas e Pais/Responsáveis.

- **Por que decidimos fazer esse projeto?** Para facilitar a comunicação e o acompanhamento de questionários e evolução clínica de forma centralizada e ágil.
- **Quais foram os desafios de implementá-lo?** Integrar um frontend moderno (Vite + HTMX) com o ecosistema do Django mantendo tudo otimizado, além de criar perfis de usuário com diferentes níveis de acesso.
- **O que aprendemos com ele?** A orquestrar ferramentas robustas (Celery, Redis, PostgreSQL) junto ao Django e criar uma experiência fluida no frontend sem depender de frameworks SPA pesados.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

### Feito com

* ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
* ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
* ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
* ![HTMX](https://img.shields.io/badge/htmx-%233366cc.svg?style=for-the-badge&logo=htmx&logoColor=white)
* ![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
* ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Arquitetura

A arquitetura do Sono é monolítica mas com separação clara entre a camada de apresentação e os serviços de background, utilizando tecnologias modernas.

```mermaid
graph TD
    Client[Browser / HTMX] -->|HTTP Requests| Django(Django App)
    Django -->|Reads/Writes| DB[(PostgreSQL)]
    Django -->|Queues Tasks| Redis[(Redis)]
    Redis -->|Processes Tasks| Celery(Celery Workers)
    Django -.->|Static/Media| S3[AWS S3 / WhiteNoise]
    Django -.->|Emails| SES[AWS SES]
```

**Django 6.0**
*É o core da aplicação, responsável por toda a regra de negócio, roteamento e ORM. A facilidade de desenvolver com Python nos deu enorme produtividade, e o Django traz "baterias inclusas" como painel de administração e segurança nativa.*

**HTMX + Alpine.js + Vite**
*Para o frontend, optamos por HTMX para manter o estado no servidor enquanto providenciamos uma experiência fluida (SPA-like). O Alpine.js cuida de interações locais simples. O Vite agrupa nossos assets (Tailwind CSS 4 + DaisyUI 5) rapidamente.*

**PostgreSQL & Redis**
*PostgreSQL é o nosso banco de dados relacional robusto. O Redis funciona como nosso message broker para o Celery (background tasks como envio de e-mail e processamento assíncrono).*

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Features

Aqui você descreve as principais features do sistema, com fluxo da feature em diagramas:

1. Autenticação e Login:
```mermaid
sequenceDiagram
    actor Usuario as Usuário
    participant Frontend as Frontend (HTMX)
    participant Backend as Django
    participant DB as Banco de Dados
    
    Usuario->>Frontend: Insere e-mail e senha
    Frontend->>Backend: POST /login
    Backend->>DB: Consulta credenciais
    DB-->>Backend: Confirmação de Acesso
    Backend-->>Frontend: Retorna fragmento com a sessão (Redirect)
    Frontend-->>Usuario: Redireciona para o painel de acordo com o perfil
```

2. Preenchimento de Questionários (Responsáveis):
```mermaid
sequenceDiagram
    actor Responsavel as Responsável
    participant Frontend as Frontend (HTMX)
    participant Backend as Django
    participant DB as Banco de Dados
    
    Responsavel->>Frontend: Seleciona dependente e preenche formulário
    Frontend->>Backend: POST /avaliacoes/nova
    Backend->>DB: Salva os dados do questionário
    DB-->>Backend: Confirmação de salvamento
    Backend-->>Frontend: Atualiza a lista de avaliações via HTMX
    Frontend-->>Responsavel: Feedback de sucesso na tela
```

3. Acompanhamento de Pacientes (Especialistas):
```mermaid
sequenceDiagram
    actor Especialista as Especialista
    participant Frontend as Frontend (HTMX)
    participant Backend as Django
    participant DB as Banco de Dados
    
    Especialista->>Frontend: Acessa o Painel
    Frontend->>Backend: GET /painel
    Backend->>DB: Busca pacientes e questionários recentes
    DB-->>Backend: Dados dos pacientes
    Backend-->>Frontend: Renderiza Tabela de Resultados
    Frontend-->>Especialista: Visualiza escores e evolução dos pacientes
```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Capturas de Tela

Aqui estão algumas visualizações da aplicação em funcionamento para os diferentes perfis:

### Autenticação e Geral
<details>
  <summary>Clique para ver as imagens de Autenticação</summary>
  <br>
  <div align="center">
    <img src="assets/screenshots/login_light.png" alt="Login Light" width="45%">
    <img src="assets/screenshots/forgot_password_light.png" alt="Esqueci a Senha" width="45%">
  </div>
</details>

### Painel do Administrador
<details>
  <summary>Clique para ver as imagens do painel Administrativo</summary>
  <br>
  <div align="center">
    <img src="assets/screenshots/admin/admin_screen_1.png" alt="Admin 1" width="45%">
    <img src="assets/screenshots/admin/admin_screen_2.png" alt="Admin 2" width="45%">
    <br>
    <img src="assets/screenshots/admin/admin_screen_3.png" alt="Admin 3" width="45%">
    <img src="assets/screenshots/admin/admin_screen_4.png" alt="Admin 4" width="45%">
    <br>
    <img src="assets/screenshots/admin/admin_screen_5.png" alt="Admin 5" width="45%">
    <img src="assets/screenshots/admin/admin_screen_6.png" alt="Admin 6" width="45%">
    <br>
    <img src="assets/screenshots/admin/admin_screen_7.png" alt="Admin 7" width="45%">
    <img src="assets/screenshots/admin/admin_screen_8.png" alt="Admin 8" width="45%">
    <br>
    <img src="assets/screenshots/admin/admin_screen_9.png" alt="Admin 9" width="45%">
    <img src="assets/screenshots/admin/admin_screen_10.png" alt="Admin 10" width="45%">
  </div>
</details>

### Visão do Responsável
<details>
  <summary>Clique para ver as imagens da área do Responsável</summary>
  <br>
  <div align="center">
    <img src="assets/screenshots/guardian/guardian_screen_1.png" alt="Responsável 1" width="45%">
    <img src="assets/screenshots/guardian/guardian_screen_2.png" alt="Responsável 2" width="45%">
    <br>
    <img src="assets/screenshots/guardian/guardian_screen_3.png" alt="Responsável 3" width="45%">
  </div>
</details>

### Visão do Especialista
<details>
  <summary>Clique para ver as imagens da área do Especialista</summary>
  <br>
  <div align="center">
    <img src="assets/screenshots/specialist/specialist_screen_1.png" alt="Especialista 1" width="45%">
    <img src="assets/screenshots/specialist/specialist_screen_2.png" alt="Especialista 2" width="45%">
    <br>
    <img src="assets/screenshots/specialist/specialist_screen_3.png" alt="Especialista 3" width="45%">
    <img src="assets/screenshots/specialist/specialist_screen_4.png" alt="Especialista 4" width="45%">
    <br>
    <img src="assets/screenshots/specialist/specialist_screen_5.png" alt="Especialista 5" width="45%">
  </div>
</details>

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Começando

Siga as instruções abaixo para configurar o projeto localmente.

### Pré-requisitos

- Python 3.14
- Node.js 24+
- PostgreSQL
- Redis
- [uv](https://docs.astral.sh/uv/)

### Instalação

1. Clone o projeto e configure o ambiente
   ```sh
   git clone https://github.com/DenPaz/sono.git
   cd sono
   cp .env.example .env
   ```
2. Instale as dependências e inicie o banco de dados
   ```sh
   make setup
   make db
   ```
3. Inicie os servidores de desenvolvimento
   ```sh
   make dev
   ```
   
O Django estará disponível em `http://localhost:8000` e o Vite em `http://localhost:5173`.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Contribuindo

Contribuições fazem com que a comunidade open source seja um lugar incrível para aprender, inspirar e criar. Qualquer contribuição que você fizer será **muito apreciada**.

Se você tem uma sugestão para melhorar o projeto, por favor, faça um fork do repositório e crie um pull request. Você também pode abrir uma issue com a tag "enhancement".
Não se esqueça de dar uma estrela ao projeto! Obrigado!

1. Faça o Fork do Projeto
2. Crie sua Branch de Feature (`git checkout -b feature/FeatureIncrivel`)
3. Faça o Commit das suas Mudanças (`git commit -m 'Adiciona uma Feature Incrível'`)
4. Faça o Push para a Branch (`git push origin feature/FeatureIncrivel`)
5. Abra um Pull Request

### Top contributors:

<a href="https://github.com/DenPaz/sono/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=DenPaz/sono" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Licença

Distribuído sob a Licença MIT. Veja `LICENSE` para mais informações.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/DenPaz/sono.svg?style=for-the-badge
[contributors-url]: https://github.com/DenPaz/sono/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/DenPaz/sono.svg?style=for-the-badge
[forks-url]: https://github.com/DenPaz/sono/network/members
[stars-shield]: https://img.shields.io/github/stars/DenPaz/sono.svg?style=for-the-badge
[stars-url]: https://github.com/DenPaz/sono/stargazers
[issues-shield]: https://img.shields.io/github/issues/DenPaz/sono.svg?style=for-the-badge
[issues-url]: https://github.com/DenPaz/sono/issues
[license-shield]: https://img.shields.io/github/license/DenPaz/sono.svg?style=for-the-badge
[license-url]: https://github.com/DenPaz/sono/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
