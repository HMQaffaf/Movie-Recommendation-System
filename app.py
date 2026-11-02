import os
import sys
import json
import urllib.parse
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from recommender import MovieRecommender

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
recommender = MovieRecommender(DATA_DIR)

class CineMatchHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        params = urllib.parse.parse_qs(parsed_url.query)

        if path in ['/', '/index.html']:
            self.serve_file(os.path.join(BASE_DIR, 'templates', 'index.html'), 'text/html; charset=utf-8')
            return

        elif path == '/api/movies':
            movies = recommender.get_all_movies()
            self.send_json({'success': True, 'count': len(movies), 'movies': movies})
            return

        elif path == '/api/trending':
            limit = int(params.get('limit', [16])[0])
            trending = recommender.get_trending_movies(limit=limit)
            self.send_json({'success': True, 'movies': trending})
            return

        elif path == '/api/genre':
            genre = params.get('name', ['Action'])[0]
            limit = int(params.get('limit', [16])[0])
            movies = recommender.get_movies_by_genre(genre, limit=limit)
            self.send_json({'success': True, 'genre': genre, 'movies': movies})
            return

        elif path == '/api/search':
            query = params.get('q', [''])[0]
            matches = recommender.search_movies(query, limit=10)
            self.send_json({'success': True, 'query': query, 'matches': matches})
            return

        elif path.startswith('/static/'):
            relative_path = path[len('/static/'):]
            full_path = os.path.join(BASE_DIR, 'static', relative_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                content_type = self.guess_type(full_path)
                self.serve_file(full_path, content_type)
                return
            else:
                self.send_error(404, "Static file not found")
                return

        self.send_error(404, "Endpoint not found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == '/api/recommend':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                titles = body.get('titles', [])
                if isinstance(titles, str):
                    titles = [titles]
                mode = body.get('mode', 'hybrid')
                top_n = int(body.get('top_n', 10))

                recommendations = recommender.recommend(titles, mode=mode, top_n=top_n)
                self.send_json({
                    'success': True,
                    'selected_titles': titles,
                    'mode': mode,
                    'count': len(recommendations),
                    'recommendations': recommendations
                })
            except Exception as e:
                self.send_json({'success': False, 'error': str(e)}, status=500)
            return

        self.send_error(404, "Endpoint not found")

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {str(e)}")

    def send_json(self, data, status=200):
        content = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

def run(port=5000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CineMatchHandler)
    url = f"http://localhost:{port}"

    print("\n" + "=" * 65)
    print("  🎬 CineMatch AI — Intelligent Movie Recommendation System")
    print(f"  🚀 Server running at: {url}")
    print("  ⭐ Built with Python, NumPy & Cosine Similarity")
    print("  👉 Opening in your default web browser automatically...")
    print("  Press Ctrl+C to stop the server anytime.")
    print("=" * 65 + "\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[CineMatch] Server stopped gracefully. Goodbye!")
        httpd.server_close()

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(port)
