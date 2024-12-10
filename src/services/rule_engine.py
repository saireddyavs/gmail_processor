import json
import logging
from src.utils import compare_dates, parse_date, parse_date_time

logger = logging.getLogger("gmail_processor")

class Rule:
    def __init__(self, rule_data):
        self.conditions = rule_data['conditions']
        self.predicate = rule_data['predicate']
        self.actions = rule_data['actions']

    def evaluate(self, email):
        condition_results = [self.evaluate_condition(cond, email) for cond in self.conditions]
        if self.predicate == 'All':
            return all(condition_results)
        elif self.predicate == 'Any':
            return any(condition_results)
        return False

    def evaluate_condition(self, condition, email):
        field = condition['field']
        predicate = condition['predicate']
        value = condition['value']

        try:
            # Handle specific field logic (e.g., received_date)
            if field == 'received_date':
                email_date = parse_date_time(email.received_date)
                comparison_date = parse_date(value['date'])
                if email_date and comparison_date:
                    return compare_dates(
                        email_date, comparison_date, predicate, 
                        value.get('unit', 'days'), value.get('value', 0)
                    )
                return False

            # General field evaluation
            email_value = email.get_field(field)
            if email_value is None:
                logger.warning(f"Field '{field}' not found on email object.")
                return False

            # Handle string-based conditions
            if isinstance(email_value, str):
                return self.apply_predicate(predicate, email_value, value)

        except Exception as e:
            logger.error(f"Error evaluating condition {condition}: {e}")
        return False

    @staticmethod
    def apply_predicate(predicate, email_value, condition_value):
        if predicate == 'Contains':
            return condition_value in email_value
        elif predicate == 'Does not Contain':
            return condition_value not in email_value
        elif predicate == 'Equals':
            return email_value == condition_value
        elif predicate == 'Does not equal':
            return email_value != condition_value
        logger.warning(f"Unsupported predicate: {predicate}")
        return False

    def __str__(self):
            conditions_str = [f"{cond['field']} {cond['predicate']} {cond['value']}" for cond in self.conditions]
            actions_str = [f"Action: {action['action']}" for action in self.actions]
            
            return f"Rule: {'All' if self.predicate == 'All' else 'Any'} of Conditions\n" + \
                "\n".join(conditions_str) + "\nActions:\n" + "\n".join(actions_str)
class RuleEngine:
    def __init__(self, rules_file, gmail_service, stop_after_first_match=True):
        self.rules = self.load_rules(rules_file)
        self.gmail_service = gmail_service
        self.stop_after_first_match = stop_after_first_match

    def load_rules(self, rules_file):
        with open(rules_file, 'r') as f:
            return [Rule(rule_data) for rule_data in json.load(f)]

    def process_email(self, email):
        for rule in self.rules:
            if rule.evaluate(email):
                logger.info(f"Rule matched: {rule.conditions}")
                # self.apply_actions(rule, email)
                if self.stop_after_first_match:
                    break

    def apply_actions(self, rule, email):
        for action in rule.actions:
            try:
                if action['action'] == 'Mark as read':
                    self.gmail_service.mark_as_read(email.id)
                    email.status = 'read'
                elif action['action'] == 'Mark as unread':
                    self.gmail_service.mark_as_unread(email.id)
                    email.status = 'unread'
                elif action['action'] == 'Move Message':
                    destination = action.get('destination')
                    self.gmail_service.move_message(email.id, destination)
                    logger.info(f"Moved email {email.id} to {destination}")
            except Exception as e:
                logger.error(f"Failed to apply action {action}: {e}")
