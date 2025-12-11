"""Application entrypoint for deployment and local usage."""

from __future__ import annotations

from bitrich import create_app

app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
