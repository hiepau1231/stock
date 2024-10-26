from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.stock_analysis.services.recommendation_service import RecommendationService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Cập nhật danh sách cổ phiếu được khuyến nghị'

    def handle(self, *args, **kwargs):
        try:
            recommendation_service = RecommendationService()
            recommendations = recommendation_service.get_top_recommendations(limit=5)
            
            # Force cập nhật cache
            cache_key = 'top_recommendations_5'
            cache.set(cache_key, recommendations, 604800)  # 1 tuần
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated recommendations for {len(recommendations)} stocks'
                )
            )
        except Exception as e:
            logger.error(f"Error updating recommendations: {str(e)}")
            self.stdout.write(
                self.style.ERROR(
                    f'Error updating recommendations: {str(e)}'
                )
            )
