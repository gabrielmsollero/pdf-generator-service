# pdf-generator-service

A microservice for generating PDF documents from templates, with a REST API interface. Conveniently designed so that adding new templates does not require changes to the code - just add a new folder inside `app/templates`, and the rest will be taken care of 😉

## How to run

Since this is intended to be a microservice, it runs on Docker. Feel free to run `compose.dev.yml` for development (Flask in debug mode) or `compose.yml` for production. You can use the environment variable `PORT` to define in which port this will be served in the host machine. Defaults to 3000.

The Docker image is also available in [Dockerhub](https://hub.docker.com/repository/docker/gabrielmsollero/pdf-generator). Just pull from there and specify your templates as the `templates` volume, and you should be good to go!

## Adding new templates

Here's how to do it:

1. Create a new folder inside `app/templates` with a suggestive name
2. Add the following files to the new folder:

   - `index.html`: your Jinja template file;
   - `style.css` _(optional)_: your stylesheet file;
   - font files _(optional)_: however you're referencing them inside your CSS file. See [examples](app/templates);
   - `schema.py`: your schema file. More on it in the next topic.

3. That's it! The worker will then create a route `/<template_name>` that will accept only `POST` requests, and will validate the request body against the schema provided. This route will return the generated PDF file, or a `400 Bad Request` if the body is not valid. Any URL that isn't a template name will return `404 Not Found`.

## The `schema.py` file

This file models the data that will be demanded from API clients and eventually passed to the Jinja template. There are two variables imported from it by the view function, and used during request processing:

- `schema`: a `marshmallow.Schema` object which, you guessed it, defines the data model;
- `additional_data`: a `dict` that will be appended to the request data before passing it to the Jinja template. This is a convenience for when there's data you want to use inside the template that won't be specified in the request body, but that also you can't specify inside the template directly. In the [letter](app/templates/letter/schema.py) template, for example, this is leveraged to specify paths of locally stored files that can't be hardcoded in the template, since they will change according to the environment.

## Testing

While developing new templates, you can use the [test](.http) file to make API requests. It's meant to be used with the [Rest Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) VSCode extension. Don't forget to adapt `@hostname` and `@port` as needed.

## Things to note

- If you really need to, you can change the default names for template and stylesheets files (`index.html` and `style.css`) in `app/config.py`.
- Jinja environments are loaded on view function definition. That means if you're working on your templates and you make only changes to HTML files you'll have to manually trigger a restart (by saving a Python file, for example). Your changes won't be reflected until then.
- You can split your CSS into multiple files if you prefer to, instead of using `style.css`. Just add their paths to `additional_data` and reference them inside your template (see [letter](app/templates/letter) example).
- You can leverage [volumes](https://docs.docker.com/engine/storage/volumes/) or [bind mounts](https://docs.docker.com/engine/storage/bind-mounts/) to make this service reusable in multiple architectures without much effort, and without even having to clone this repo at all. Just pull the [image](https://hub.docker.com/repository/docker/gabrielmsollero/pdf-generator) from Dockerhub and bind mount your templates to `/home/python/app/templates` or specify them in the `templates` volume. Isn't Docker awesome? 🤩
