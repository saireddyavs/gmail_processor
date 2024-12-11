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
        logger.debug(f"Evaluating rule with predicate '{self.predicate}' for email {email.id}")
        condition_results = [self.evaluate_condition(cond, email) for cond in self.conditions]
        result = all(condition_results) if self.predicate == 'All' else any(condition_results)
        logger.debug(f"Rule evaluation result: {result} for email {email.id}")
        return result

    def evaluate_condition(self, condition, email):
        field = condition['field']
        predicate = condition['predicate']
        value = condition['value']

        try:
            logger.debug(f"Evaluating condition: {field} {predicate} {value} for email {email.id}")
            if field == 'received_date':
                email_date = parse_date_time(email.received_date)
                comparison_date = parse_date(value['date'])
                if email_date and comparison_date:
                    result = compare_dates(
                        email_date, comparison_date, predicate,
                        value.get('unit', 'days'), value.get('value', 0)
                    )
                    logger.debug(f"Condition result for received_date: {result} for email {email.id}")
                    return result
                return False

            email_value = email.get_field(field)
            if email_value is None:
                logger.warning(f"Field '{field}' not found on email object for email {email.id}")
                return False

            if isinstance(email_value, str):
                result = self.apply_predicate(predicate, email_value, value)
                logger.debug(f"Condition result for field {field}: {result} for email {email.id}")
                return result

        except Exception as e:
            logger.error(f"Error evaluating condition {condition} for email {email.id}: {e}")
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
        logger.info(f"Loaded {len(self.rules)} rules from {rules_file}")

    def load_rules(self, rules_file):
        with open(rules_file, 'r') as f:
            rules = [Rule(rule_data) for rule_data in json.load(f)]
            logger.debug(f"Rules loaded: {rules}")
            return rules

    def process_email(self, email):
        logger.info(f"Processing email {email.id}")
        for rule in self.rules:
            if rule.evaluate(email):
                logger.info(f"Rule matched: {rule}")
                self.apply_actions(rule, email)
                if self.stop_after_first_match:
                    logger.debug(f"Stopping further rule processing for email {email.id}")
                    break
        else:
            logger.debug(f"No rules matched for email {email.id}")

    def apply_actions(self, rule, email):
        for action in rule.actions:
            try:
                logger.info(f"Applying action '{action['action']}' for email {email.id}")
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
                logger.error(f"Failed to apply action {action} for email {email.id}: {e}")
