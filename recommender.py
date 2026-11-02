import os
import re
import math
import numpy as np
import pandas as pd
from collections import Counter

class SimpleTfidf:
    """Lightweight, zero-dependency TF-IDF vectorizer using pure NumPy."""
    def __init__(self, max_features=1500, min_df=1):
        self.max_features = max_features
        self.min_df = min_df
        self.vocabulary_ = {}
        self.idf_ = None

    def _tokenize(self, text):
        return re.findall(r'[a-zA-Z0-9]+', str(text).lower())

    def fit_transform(self, documents):
        doc_tokens = [self._tokenize(doc) for doc in documents]
        N = len(documents)
        
        # Calculate document frequency
        df_counts = Counter()
        for tokens in doc_tokens:
            unique_tokens = set(tokens)
            df_counts.update(unique_tokens)
            
        # Select top features
        filtered_words = [word for word, count in df_counts.items() if count >= self.min_df and len(word) > 2]
        sorted_words = sorted(filtered_words, key=lambda w: (-df_counts[w], w))[:self.max_features]
        self.vocabulary_ = {word: idx for idx, word in enumerate(sorted_words)}
        
        # Compute IDF
        self.idf_ = np.zeros(len(self.vocabulary_))
        for word, idx in self.vocabulary_.items():
            # Standard smoothed IDF formula
            self.idf_[idx] = math.log((1 + N) / (1 + df_counts[word])) + 1.0
            
        # Compute TF-IDF matrix
        matrix = np.zeros((N, len(self.vocabulary_)), dtype=np.float32)
        for i, tokens in enumerate(doc_tokens):
            if not tokens:
                continue
            tf_counter = Counter(tokens)
            for word, count in tf_counter.items():
                if word in self.vocabulary_:
                    j = self.vocabulary_[word]
                    matrix[i, j] = count * self.idf_[j]
                    
            # L2 normalize row
            norm = np.linalg.norm(matrix[i])
            if norm > 0:
                matrix[i] /= norm
                
        return matrix

class MovieRecommender:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            
        self.movies_path = os.path.join(data_dir, 'movies.csv')
        self.ratings_path = os.path.join(data_dir, 'ratings.csv')
        
        self.load_data()
        self.train_content_model()
        self.train_collaborative_model()

    def load_data(self):
        self.movies = pd.read_csv(self.movies_path)
        self.ratings = pd.read_csv(self.ratings_path)
        self.movies['clean_title'] = self.movies['title'].str.strip()
        self.title_to_id = dict(zip(self.movies['clean_title'], self.movies['movieId']))
        self.id_to_movie = self.movies.set_index('movieId').to_dict('index')

    def train_content_model(self):
        def create_soup(row):
            genres = " ".join(str(row['genres']).split('|'))
            director = str(row['director']).replace(' ', '_')
            overview = str(row['overview'])
            return f"{genres} {genres} {genres} {director} {overview}"

        self.movies['soup'] = self.movies.apply(create_soup, axis=1)
        self.tfidf = SimpleTfidf(max_features=2000)
        self.tfidf_matrix = self.tfidf.fit_transform(self.movies['soup'].tolist())
        
        # Content Cosine Similarity: A @ A.T (since rows are L2 normalized, dot product = cosine similarity)
        self.content_sim = np.dot(self.tfidf_matrix, self.tfidf_matrix.T)
        self.movie_idx_map = pd.Series(self.movies.index, index=self.movies['movieId']).drop_duplicates()

    def train_collaborative_model(self):
        self.movie_user_matrix = self.ratings.pivot(index='movieId', columns='userId', values='rating').fillna(0)
        
        # Vectorized normalized Cosine Similarity for Collaborative Filtering
        matrix_vals = self.movie_user_matrix.values.astype(np.float32)
        norms = np.linalg.norm(matrix_vals, axis=1, keepdims=True)
        norms[norms == 0] = 1e-9
        normalized_matrix = matrix_vals / norms
        self.collab_sim_matrix = np.dot(normalized_matrix, normalized_matrix.T)
        self.collab_id_map = {mid: idx for idx, mid in enumerate(self.movie_user_matrix.index)}

    def search_movies(self, query, limit=8):
        if not query:
            return []
        q = query.lower().strip()
        matches = []
        for title in self.movies['title']:
            if q in title.lower():
                matches.append(title)
            if len(matches) >= limit:
                break
        return matches

    def get_all_movies(self):
        return self._format_results(self.movies['movieId'].tolist())

    def get_trending_movies(self, limit=12):
        sorted_movies = self.movies.sort_values(by='rating', ascending=False).head(limit)
        return self._format_results(sorted_movies['movieId'].tolist(), scores=None)

    def get_movies_by_genre(self, genre, limit=12):
        filtered = self.movies[self.movies['genres'].str.contains(genre, case=False, na=False)]
        sorted_movies = filtered.sort_values(by='rating', ascending=False).head(limit)
        return self._format_results(sorted_movies['movieId'].tolist(), scores=None)

    def recommend(self, selected_titles, mode='hybrid', top_n=8):
        if isinstance(selected_titles, str):
            selected_titles = [selected_titles]
            
        target_ids = []
        for title in selected_titles:
            t_clean = title.strip()
            if t_clean in self.title_to_id:
                target_ids.append(self.title_to_id[t_clean])
            else:
                for m_title, m_id in self.title_to_id.items():
                    if t_clean.lower() in m_title.lower():
                        target_ids.append(m_id)
                        break
                        
        if not target_ids:
            return []
            
        num_movies = len(self.movies)
        content_scores = np.zeros(num_movies)
        collab_scores = np.zeros(num_movies)
        
        for m_id in target_ids:
            if m_id in self.movie_idx_map:
                idx = self.movie_idx_map[m_id]
                content_scores += self.content_sim[idx]
        content_scores /= len(target_ids)
        
        valid_collab = [m_id for m_id in target_ids if m_id in self.collab_id_map]
        if valid_collab:
            for m_id in valid_collab:
                c_idx = self.collab_id_map[m_id]
                collab_scores += self.collab_sim_matrix[c_idx]
            collab_scores /= len(valid_collab)
        else:
            collab_scores = content_scores.copy()
            
        if mode == 'content':
            final_scores = content_scores
        elif mode == 'collaborative':
            final_scores = collab_scores
        else:
            final_scores = (0.55 * content_scores) + (0.45 * collab_scores)
            
        ranked_indices = np.argsort(final_scores)[::-1]
        
        recommended_ids = []
        recommended_scores = []
        
        for idx in ranked_indices:
            m_id = self.movies.iloc[idx]['movieId']
            if m_id not in target_ids:
                recommended_ids.append(m_id)
                raw_score = float(final_scores[idx])
                # Scale naturally to match percentage: 70% to 99%
                match_pct = int(min(99, max(70, (raw_score * 45) + 54)))
                recommended_scores.append(match_pct)
                
            if len(recommended_ids) >= top_n:
                break
                
        return self._format_results(recommended_ids, recommended_scores)

    def _format_results(self, movie_ids, scores=None):
        results = []
        for i, m_id in enumerate(movie_ids):
            if m_id in self.id_to_movie:
                m = self.id_to_movie[m_id].copy()
                m['movieId'] = int(m_id)
                m['genres_list'] = str(m['genres']).split('|')
                m['match_score'] = scores[i] if scores else None
                results.append(m)
        return results

if __name__ == '__main__':
    rec = MovieRecommender('build_cinematch/CineMatch-Movie-Recommender/data')
    print('Testing recommendation for Inception (2010):')
    for m in rec.recommend(['Inception (2010)'], mode='hybrid', top_n=5):
        print(f" -> {m['title']} | {m['match_score']}% Match | {m['genres']}")
