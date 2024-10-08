import json
import urllib

def lambda_handler(event, context):
    domain = 'https://a-arbeitsrecht.de' 
    routes = [
        {'path': '/', 'priority': 1.0, 'changefreq': 'weekly'},
        {'path': '/aktuelles', 'priority': 0.9, 'changefreq': 'weekly'},
    ]

    try:
        dynamic_routes = get_dynamic_routes()
        routes.extend(dynamic_routes)
    except Exception as e:
        print(f"Error fetching dynamic routes: {e}")

    # Sitemap XML erstellen
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for route in routes:
        xml += f'  <url>\n'
        xml += f'    <loc>{domain}{route["path"]}</loc>\n'
        xml += f'    <changefreq>{route["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{route["priority"]}</priority>\n'
        xml += f'  </url>\n'

    xml += '</urlset>'

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/xml'
        },
        'body': xml
    }

def get_dynamic_routes(tenant: str):
    url = 'https://a-arbeitsrecht.de/api/blog-ids'
    headers = {
        'x-tenant-id': tenant
    }

    # Erstelle die Anfrage
    req = urllib.request.Request(url, headers=headers)

    try:
        # Sende die Anfrage und erhalte die Antwort
        with urllib.request.urlopen(req) as response:
            response_body = response.read()
            data = json.loads(response_body)
            
            dynamic_routes = []
            # Angenommen, die API gibt eine Liste von Blog-Posts zurück
            for item in data:
                path = f"/blog/{item['slug']}"  # Beispiel: /blog/slug
                dynamic_routes.append({
                'path': path,
                'priority': 0.9,
                'changefreq': 'weekly'
            })
            return dynamic_routes
    except urllib.error.HTTPError as e:
        return []
    except Exception as e:
        return []
    url = 'https://a-arbeitsrecht.de/api/blog-ids'
    headers = {
        'tenant-id': 'a-arbeitsrecht.de'
    }
