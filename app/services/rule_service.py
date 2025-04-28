import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml
from fastapi import HTTPException

from app.core.config import settings
from app.models.report import TransformationRule, TransformationRuleSet


def get_rule_set(rule_set_id: Optional[str] = None) -> TransformationRuleSet:
    """
    Get a rule set by ID. If no ID is provided, return the default rule set.
    """
    # If no rules file exists, create the default one
    if not os.path.exists(settings.RULES_FILE):
        _create_default_rules()
    
    # Load all rule sets
    with open(settings.RULES_FILE, "r") as f:
        rule_sets = yaml.safe_load(f) or {}
    
    # If no rule set ID is provided, use the latest one
    if not rule_set_id:
        if not rule_sets:
            _create_default_rules()
            with open(settings.RULES_FILE, "r") as f:
                rule_sets = yaml.safe_load(f) or {}
        
        # Get the latest version
        latest_version = max(rule_sets.keys())
        rule_set_id = latest_version
    
    # Check if the rule set exists
    if rule_set_id not in rule_sets:
        raise HTTPException(status_code=404, detail=f"Rule set not found: {rule_set_id}")
    
    # Convert to model
    rules_data = rule_sets[rule_set_id]
    rules = [
        TransformationRule(
            output_field=rule["output_field"],
            expression=rule["expression"],
            description=rule.get("description", "")
        )
        for rule in rules_data["rules"]
    ]
    
    return TransformationRuleSet(
        rules=rules,
        version=rule_set_id,
        updated_at=datetime.fromisoformat(rules_data["updated_at"])
    )


def update_rule_set(rule_set: TransformationRuleSet) -> TransformationRuleSet:
    """
    Update an existing rule set or create a new one.
    """
    # Load existing rule sets
    if os.path.exists(settings.RULES_FILE):
        with open(settings.RULES_FILE, "r") as f:
            rule_sets = yaml.safe_load(f) or {}
    else:
        rule_sets = {}
    
    # Create new version if not updating an existing one
    version = rule_set.version
    if not version or version not in rule_sets:
        # Generate a new version based on timestamp
        version = datetime.now().strftime("%Y%m%d%H%M%S")
        rule_set.version = version
    
    # Update the rule set
    rule_sets[version] = {
        "rules": [
            {
                "output_field": rule.output_field,
                "expression": rule.expression,
                "description": rule.description
            }
            for rule in rule_set.rules
        ],
        "updated_at": rule_set.updated_at.isoformat()
    }
    
    # Save to file
    with open(settings.RULES_FILE, "w") as f:
        yaml.dump(rule_sets, f)
    
    return rule_set


def _create_default_rules() -> None:
    """
    Create the default transformation rules based on the requirements.
    """
    default_rules = [
        TransformationRule(
            output_field="outfield1",
            expression="field1 + field2",
            description="Concatenate field1 and field2"
        ),
        TransformationRule(
            output_field="outfield2",
            expression="refdata1",
            description="Use refdata1 directly"
        ),
        TransformationRule(
            output_field="outfield3",
            expression="refdata2 + refdata3",
            description="Concatenate refdata2 and refdata3"
        ),
        TransformationRule(
            output_field="outfield4",
            expression="field3 * max(field5, refdata4)",
            description="Multiply field3 by the maximum of field5 and refdata4"
        ),
        TransformationRule(
            output_field="outfield5",
            expression="max(field5, refdata4)",
            description="Maximum of field5 and refdata4"
        )
    ]
    
    rule_set = TransformationRuleSet(
        rules=default_rules,
        version="default",
        updated_at=datetime.now()
    )
    
    update_rule_set(rule_set)


def parse_expression(expression: str, row: Dict[str, Any]) -> Any:
    """
    Parse and evaluate a transformation rule expression.
    
    This is a simplified expression parser that supports:
    - Field references (e.g., field1, refdata1)
    - Basic operations (+, -, *, /)
    - Function calls (max, min, etc.)
    
    In a production environment, this would be replaced with a more robust
    expression parser or a rules engine.
    """
    # Replace field references with dictionary lookups
    modified_expression = expression
    for field in re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expression):
        if field in row and field not in ['max', 'min']:
            # Get the value from the row
            value = row[field]
            
            # If the value is a string, wrap it in quotes
            if isinstance(value, str):
                replacement = f"'{value}'"
            else:
                replacement = str(value)
            
            # Replace the field with its value
            modified_expression = re.sub(r'\b' + field + r'\b', replacement, modified_expression)
    
    # Evaluate the expression
    try:
        # Define safe functions
        safe_dict = {
            'max': max,
            'min': min,
            'len': len,
            'str': str,
            'int': int,
            'float': float
        }
        
        # Evaluate the expression in a safe context
        result = eval(modified_expression, {"__builtins__": {}}, safe_dict)
        return result
    except Exception as e:
        # In a production environment, we would log this error
        return f"Error: {str(e)}"
