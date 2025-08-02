class TransformationError(Exception):
    """Base exception for transformation errors"""

    pass


class MostExpensiveTransformationError(TransformationError):
    """Error during MostExpensive transformation"""

    pass


class OdsUsersTransformationError(TransformationError):
    """Error during OdsUsers transformation"""

    pass


class UserProcessingError(TransformationError):
    """Error when processing individual user"""

    pass
