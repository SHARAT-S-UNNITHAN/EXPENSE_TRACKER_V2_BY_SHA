from pathlib import Path

import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATASET_PATH = Path(__file__).resolve().parent.parent / 'dataset.csv'


def preprocess_text(value):
    if not isinstance(value, str):
        return ''
    tokens = word_tokenize(value.lower())
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
    return ' '.join(tokens)


class PredictCategory(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        description = request.data.get('description')
        if not isinstance(description, str) or not description.strip() or len(description) > 500:
            return Response(
                {'detail': 'Provide a description between 1 and 500 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = pd.read_csv(DATASET_PATH)
            if not {'clean_description', 'category'}.issubset(data.columns) or data.empty:
                return Response({'detail': 'The category dataset is unavailable.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            vectorizer = TfidfVectorizer()
            features = vectorizer.fit_transform(data['clean_description'].fillna('').astype(str))
            user_vector = vectorizer.transform([preprocess_text(description)])
            similarities = cosine_similarity(user_vector, features)
            closest_index = similarities.argmax()
            predicted_category = data.iloc[closest_index]['category']
            return Response({'predicted_category': str(predicted_category)}, status=status.HTTP_200_OK)
        except (OSError, ValueError, KeyError) as exc:
            return Response({'detail': 'Category prediction is temporarily unavailable.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class UpdateDataset(APIView):
    # Dataset changes are administrative maintenance, never a public user action.
    permission_classes = [IsAdminUser]

    def post(self, request):
        new_data = request.data.get('new_data')
        if not isinstance(new_data, dict):
            return Response({'detail': 'new_data must be an object.'}, status=status.HTTP_400_BAD_REQUEST)

        description = new_data.get('description')
        category = new_data.get('category')
        if not isinstance(description, str) or not description.strip() or len(description) > 500:
            return Response({'detail': 'Description must contain 1 to 500 characters.'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(category, str) or not category.strip() or len(category) > 100:
            return Response({'detail': 'Category must contain 1 to 100 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = pd.read_csv(DATASET_PATH)
            if not {'description', 'category', 'clean_description'}.issubset(data.columns):
                return Response({'detail': 'Dataset schema is invalid.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            row = {
                'description': description.strip(),
                'category': category.strip(),
                'clean_description': preprocess_text(description),
            }
            data = pd.concat([data, pd.DataFrame([row])], ignore_index=True)
            data.to_csv(DATASET_PATH, index=False)
        except (OSError, ValueError) as exc:
            return Response({'detail': 'Dataset could not be updated.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'Dataset updated.'}, status=status.HTTP_200_OK)
