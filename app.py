from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weights.db'
db = SQLAlchemy(app)


class Weight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Weight {self.weight}>"


def initialize_database():
    """
    Initialize the database and create all tables.
    """

    with app.app_context():
        db.create_all()


weights = [0.5, 1, 1.5, 2, 10, 20, 30, 50, 90]


def find_combination(desired_weight, weights):
    """
    Find the combination of weights that comes closest to the desired weight.

    Args:
        desired_weight (float): The desired weight.
        weights (list): The available weights.

    Returns:
        tuple: A tuple containing the combination of weights and the difference between
        the desired weight and the total weight.
    """
    # Sort the weights in descending order to prioritize larger weights first
    weights.sort(reverse=True)
    combination = []
    total_weight = 35  # weight of the barbell

    for weight in weights:
        individual_weight = (
            int(weight / 2) if weight % 2 == 0 else weight / 2
        )  # weight of each side of the barbell
        if total_weight + weight <= desired_weight:
            combination.append(individual_weight)
            total_weight += weight

    difference = abs(desired_weight - total_weight)
    return combination, difference


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Handle the home page, including weight calculation and saving entries.

    Raises:
        ValueError: Raised when the desired weight is less than 35 lbs.

    Returns:
        Response: The response for the home page.
    """
    if request.method == 'POST':
        try:
            desired_weight = float(request.form['desired_weight'])
            if desired_weight < 35:
                raise ValueError(
                    "Weight cannot be less than the weight of the bar (35 lbs)"
                )

            best_combination, difference = find_combination(desired_weight, weights)

            weight_entry = Weight(weight=desired_weight)
            db.session.add(weight_entry)
            db.session.commit()

            return redirect(url_for('result', desired_weight=desired_weight))
        except ValueError as e:
            error_message = str(e)
            saved_weights = get_saved_weights()
            return render_template(
                'index.html',
                weights=weights,
                error_message=error_message,
                saved_weights=saved_weights,
            )
    else:
        saved_weights = get_saved_weights()
        return render_template(
            'index.html', weights=weights, saved_weights=saved_weights
        )


@app.route('/result/<float:desired_weight>')
def result(desired_weight):
    """
    Show the result page with the calculated weight combination and difference.

    Args:
        desired_weight (float): The desired weight.

    Returns:
        Response: The response for the result page.
    """
    best_combination, difference = find_combination(desired_weight, weights)
    return render_template(
        'result.html',
        desired_weight=desired_weight,
        best_combination=best_combination,
        difference=difference,
    )


def get_saved_weights():
    """
    Retrieve the saved weights from the database.

    Returns:
        list: A list of saved weights.
    """
    return Weight.query.order_by(Weight.id.desc()).limit(5).all()

@app.route("/clear_weights", methods=["POST"])
def clear_weights():
    """
    Clear all saved weights from the database.
    Returns:
        Response: The response for the home page.
    """
    Weight.query.delete()
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == '__main__':
    initialize_database()
    app.run(
        host='192.168.4.24', port=8000, debug=True, use_reloader=True, threaded=True
    )
