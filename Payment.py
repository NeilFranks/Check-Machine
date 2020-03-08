class Payment(object):
    def __init__(
        self, customer_account_no, last_name, first_name, trace_no, amount, address
    ):
        self.customer_account_no = customer_account_no
        self.last_name = last_name
        self.first_name = first_name
        self.trace_no = trace_no
        self.amount = amount
        self.address = address
        self.customer_name = first_name + " " + last_name

    def set_customer_account_no(self, customer_account_no):
        self.customer_account_no = customer_account_no

    def set_customer_name(self, customer_name):
        self.customer_name = customer_name

    def set_trace_no(self, trace_no):
        self.trace_no = trace_no

    def set_amount(self, amount):
        self.amount = amount

    def set_address(self, address):
        self.address = address
