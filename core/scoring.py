"""
Offer Scoring System

Evaluation logic for offers and quotes in the ASI system.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ScoringCriteria:
    """Scoring criteria definition."""
    name: str
    weight: float
    min_score: float
    max_score: float
    description: str


@dataclass
class ScoreResult:
    """Score result with breakdown."""
    total_score: float
    criteria_scores: Dict[str, float]
    recommendation: str
    confidence: float
    reasoning: str


class OfferScorer:
    """Offer scoring system with configurable criteria."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("offer_scorer")
        
        # Scoring configuration
        self.criteria = self._initialize_criteria()
        self.scoring_weights = self._initialize_weights()
        self.thresholds = self._initialize_thresholds()
        
        self.logger.info(f"OfferScorer initialized with {len(self.criteria)} criteria")
    
    def _initialize_criteria(self) -> List[ScoringCriteria]:
        """Initialize scoring criteria."""
        return [
            ScoringCriteria(
                name="price",
                weight=0.4,
                min_score=0.0,
                max_score=1.0,
                description="Price competitiveness and value"
            ),
            ScoringCriteria(
                name="quality",
                weight=0.3,
                min_score=0.0,
                max_score=1.0,
                description="Product/service quality and specifications"
            ),
            ScoringCriteria(
                name="delivery",
                weight=0.2,
                min_score=0.0,
                max_score=1.0,
                description="Delivery time and reliability"
            ),
            ScoringCriteria(
                name="reputation",
                weight=0.1,
                min_score=0.0,
                max_score=1.0,
                description="Supplier reputation and track record"
            )
        ]
    
    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize scoring weights."""
        return {
            "price": 0.4,
            "quality": 0.3,
            "delivery": 0.2,
            "reputation": 0.1
        }
    
    def _initialize_thresholds(self) -> Dict[str, float]:
        """Initialize scoring thresholds."""
        return {
            "accept": 0.8,
            "negotiate": 0.5,
            "reject": 0.0
        }
    
    def score_offer(self, offer_data: Dict[str, Any]) -> ScoreResult:
        """Score an offer and return detailed results."""
        try:
            # Extract offer components
            price_data = offer_data.get("pricing", {})
            quality_data = offer_data.get("quality", {})
            delivery_data = offer_data.get("delivery", {})
            reputation_data = offer_data.get("reputation", {})
            
            # Calculate individual scores
            price_score = self._score_price(price_data, offer_data)
            quality_score = self._score_quality(quality_data, offer_data)
            delivery_score = self._score_delivery(delivery_data, offer_data)
            reputation_score = self._score_reputation(reputation_data, offer_data)
            
            # Calculate weighted total
            total_score = (
                price_score * self.scoring_weights["price"] +
                quality_score * self.scoring_weights["quality"] +
                delivery_score * self.scoring_weights["delivery"] +
                reputation_score * self.scoring_weights["reputation"]
            )
            
            # Determine recommendation
            recommendation = self._determine_recommendation(total_score)
            
            # Calculate confidence
            confidence = self._calculate_confidence(price_score, quality_score, delivery_score, reputation_score)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(price_score, quality_score, delivery_score, reputation_score)
            
            return ScoreResult(
                total_score=total_score,
                criteria_scores={
                    "price": price_score,
                    "quality": quality_score,
                    "delivery": delivery_score,
                    "reputation": reputation_score
                },
                recommendation=recommendation,
                confidence=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"Failed to score offer: {e}")
            return ScoreResult(
                total_score=0.0,
                criteria_scores={},
                recommendation="reject",
                confidence=0.0,
                reasoning=f"Scoring error: {e}"
            )
    
    def _score_price(self, price_data: Dict[str, Any], offer_data: Dict[str, Any]) -> float:
        """Score price component."""
        try:
            # Get base price
            base_price = price_data.get("total", 0.0)
            if base_price <= 0:
                return 0.0
            
            # Get market benchmark (placeholder)
            market_benchmark = self._get_market_benchmark(offer_data)
            if market_benchmark <= 0:
                return 0.5  # Default score if no benchmark
            
            # Calculate price competitiveness
            price_ratio = base_price / market_benchmark
            
            # Score based on ratio (lower is better)
            if price_ratio <= 0.8:
                return 1.0  # Excellent price
            elif price_ratio <= 1.0:
                return 0.8  # Good price
            elif price_ratio <= 1.2:
                return 0.6  # Fair price
            elif price_ratio <= 1.5:
                return 0.4  # High price
            else:
                return 0.2  # Very high price
                
        except Exception as e:
            self.logger.error(f"Failed to score price: {e}")
            return 0.0
    
    def _score_quality(self, quality_data: Dict[str, Any], offer_data: Dict[str, Any]) -> float:
        """Score quality component."""
        try:
            # Get quality metrics
            certifications = quality_data.get("certifications", [])
            specifications = quality_data.get("specifications", {})
            warranty = quality_data.get("warranty", 0)
            
            score = 0.0
            
            # Certification score
            if certifications:
                cert_score = min(len(certifications) * 0.2, 0.6)
                score += cert_score
            
            # Specification score
            if specifications:
                spec_score = min(len(specifications) * 0.1, 0.3)
                score += spec_score
            
            # Warranty score
            if warranty > 0:
                warranty_score = min(warranty / 24, 0.3)  # Max 2 years
                score += warranty_score
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Failed to score quality: {e}")
            return 0.0
    
    def _score_delivery(self, delivery_data: Dict[str, Any], offer_data: Dict[str, Any]) -> float:
        """Score delivery component."""
        try:
            # Get delivery metrics
            delivery_time = delivery_data.get("days", 30)
            reliability = delivery_data.get("reliability", 0.95)
            tracking = delivery_data.get("tracking", False)
            
            score = 0.0
            
            # Delivery time score (shorter is better)
            if delivery_time <= 7:
                score += 0.5
            elif delivery_time <= 14:
                score += 0.4
            elif delivery_time <= 30:
                score += 0.3
            else:
                score += 0.1
            
            # Reliability score
            score += reliability * 0.3
            
            # Tracking score
            if tracking:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Failed to score delivery: {e}")
            return 0.0
    
    def _score_reputation(self, reputation_data: Dict[str, Any], offer_data: Dict[str, Any]) -> float:
        """Score reputation component."""
        try:
            # Get reputation metrics
            rating = reputation_data.get("rating", 0.0)
            reviews_count = reputation_data.get("reviews_count", 0)
            years_in_business = reputation_data.get("years_in_business", 0)
            
            score = 0.0
            
            # Rating score
            if rating > 0:
                score += rating * 0.4
            
            # Reviews count score
            if reviews_count > 0:
                reviews_score = min(reviews_count / 100, 0.3)
                score += reviews_score
            
            # Experience score
            if years_in_business > 0:
                experience_score = min(years_in_business / 10, 0.3)
                score += experience_score
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Failed to score reputation: {e}")
            return 0.0
    
    def _get_market_benchmark(self, offer_data: Dict[str, Any]) -> float:
        """Get market benchmark price (placeholder)."""
        # This would typically query market data or historical prices
        # For now, return a placeholder value
        return 1000.0
    
    def _determine_recommendation(self, total_score: float) -> str:
        """Determine recommendation based on total score."""
        if total_score >= self.thresholds["accept"]:
            return "accept"
        elif total_score >= self.thresholds["negotiate"]:
            return "negotiate"
        else:
            return "reject"
    
    def _calculate_confidence(self, price_score: float, quality_score: float, 
                             delivery_score: float, reputation_score: float) -> float:
        """Calculate confidence in the scoring."""
        # Confidence is based on how consistent the scores are
        scores = [price_score, quality_score, delivery_score, reputation_score]
        variance = sum((score - sum(scores)/len(scores))**2 for score in scores) / len(scores)
        confidence = max(0.0, 1.0 - variance)
        return min(confidence, 1.0)
    
    def _generate_reasoning(self, price_score: float, quality_score: float,
                           delivery_score: float, reputation_score: float) -> str:
        """Generate reasoning for the score."""
        reasoning_parts = []
        
        if price_score >= 0.8:
            reasoning_parts.append("Excellent pricing")
        elif price_score >= 0.6:
            reasoning_parts.append("Competitive pricing")
        else:
            reasoning_parts.append("High pricing")
        
        if quality_score >= 0.8:
            reasoning_parts.append("High quality standards")
        elif quality_score >= 0.6:
            reasoning_parts.append("Good quality")
        else:
            reasoning_parts.append("Quality concerns")
        
        if delivery_score >= 0.8:
            reasoning_parts.append("Fast delivery")
        elif delivery_score >= 0.6:
            reasoning_parts.append("Reasonable delivery")
        else:
            reasoning_parts.append("Slow delivery")
        
        if reputation_score >= 0.8:
            reasoning_parts.append("Excellent reputation")
        elif reputation_score >= 0.6:
            reasoning_parts.append("Good reputation")
        else:
            reasoning_parts.append("Limited reputation")
        
        return "; ".join(reasoning_parts)
    
    def compare_offers(self, offers: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], ScoreResult]]:
        """Compare multiple offers and return ranked results."""
        try:
            scored_offers = []
            
            for offer in offers:
                score_result = self.score_offer(offer)
                scored_offers.append((offer, score_result))
            
            # Sort by total score (descending)
            scored_offers.sort(key=lambda x: x[1].total_score, reverse=True)
            
            return scored_offers
            
        except Exception as e:
            self.logger.error(f"Failed to compare offers: {e}")
            return []
    
    def get_scoring_criteria(self) -> List[Dict[str, Any]]:
        """Get scoring criteria information."""
        return [
            {
                "name": criteria.name,
                "weight": criteria.weight,
                "min_score": criteria.min_score,
                "max_score": criteria.max_score,
                "description": criteria.description
            }
            for criteria in self.criteria
        ]
    
    def update_criteria_weights(self, new_weights: Dict[str, float]) -> bool:
        """Update scoring criteria weights."""
        try:
            # Validate weights
            total_weight = sum(new_weights.values())
            if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
                self.logger.error(f"Total weight must be 1.0, got {total_weight}")
                return False
            
            # Update weights
            self.scoring_weights.update(new_weights)
            
            # Update criteria objects
            for criteria in self.criteria:
                if criteria.name in new_weights:
                    criteria.weight = new_weights[criteria.name]
            
            self.logger.info(f"Updated scoring weights: {new_weights}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update criteria weights: {e}")
            return False

