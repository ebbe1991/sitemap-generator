import json
import urllib
import os
import urllib.request
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.event_handler import Response


DOMAIN = os.getenv("DOMAIN")
TENANT = os.getenv("TENANT")
DYNAMIC_BLOG_ROUTES_URL = os.getenv("DYNAMIC_BLOG_ROUTES_URL")
DYNAMIC_BLOG_PREFIX = os.getenv("DYNAMIC_BLOG_PREFIX")
PAGES = os.getenv("PAGES")
app = APIGatewayHttpResolver()


def handle(event: dict, context: dict):
    return app.resolve(event, context)


@app.get("/api/sitemap")
def get():
    routes = [
        {"path": "/", "priority": 1.0, "changefreq": "weekly"},
    ]

    for page in json.loads(PAGES):
        routes.append({"path": f"/{page}", "priority": 0.9, "changefreq": "weekly"})

    if DYNAMIC_BLOG_ROUTES_URL is not None:
        try:
            dynamic_routes = get_dynamic_blog_routes(
                tenant=TENANT, prefix=DYNAMIC_BLOG_PREFIX, url=DYNAMIC_BLOG_ROUTES_URL
            )
            routes.extend(dynamic_routes)
        except Exception as e:
            print(f"Error fetching dynamic routes: {e}")

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for route in routes:
        xml += f"  <url>\n"
        xml += f'    <loc>{DOMAIN}{route["path"]}</loc>\n'
        xml += f'    <changefreq>{route["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{route["priority"]}</priority>\n'
        xml += f"  </url>\n"

    xml += "</urlset>"

    return Response(status_code=200, content_type="application/xml", body=xml)


def get_dynamic_blog_routes(tenant, prefix, url):
    headers = {"x-tenant-id": tenant}

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read()
            data = json.loads(response_body)

            dynamic_routes = []
            for item in data:
                path = f"/{prefix}/{item}"
                dynamic_routes.append(
                    {"path": path, "priority": 0.9, "changefreq": "weekly"}
                )
            return dynamic_routes
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.reason}")
        return []
    except Exception as e:
        print(f"General Error: {str(e)}")
        return []
