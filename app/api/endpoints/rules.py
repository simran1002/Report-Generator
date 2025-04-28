from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_active_user
from app.models.report import TransformationRule, TransformationRuleSet
from app.models.user import User
from app.services.rule_service import get_rule_set, update_rule_set

router = APIRouter()


@router.get("", response_model=TransformationRuleSet)
async def get_rules(
    rule_set_id: str = None,
    current_user: User = Depends(get_current_active_user)
) -> TransformationRuleSet:
    """
    Get transformation rules.
    
    Args:
        rule_set_id: The ID of the rule set to get (optional)
        current_user: The current user
    
    Returns:
        TransformationRuleSet: The rule set
    """
    try:
        return get_rule_set(rule_set_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rules: {str(e)}")


@router.post("", response_model=TransformationRuleSet)
async def update_rules(
    rule_set: TransformationRuleSet,
    current_user: User = Depends(get_current_active_user)
) -> TransformationRuleSet:
    """
    Update transformation rules.
    
    Args:
        rule_set: The rule set to update
        current_user: The current user
    
    Returns:
        TransformationRuleSet: The updated rule set
    """
    try:
        return update_rule_set(rule_set)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update rules: {str(e)}")


@router.post("/validate", response_model=dict)
async def validate_rule(
    rule: TransformationRule,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Validate a transformation rule.
    
    Args:
        rule: The rule to validate
        current_user: The current user
    
    Returns:
        dict: Validation result
    """
    # This is a simplified validation
    # In a production environment, this would be more robust
    try:
        # Check if the expression is valid
        # For simplicity, we just check if it contains basic operations
        valid_operators = ["+", "-", "*", "/", "max", "min"]
        valid = any(op in rule.expression for op in valid_operators)
        
        return {
            "valid": valid,
            "message": "Rule is valid" if valid else "Rule expression is not valid"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }
