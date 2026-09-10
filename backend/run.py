from app import create_app

app = create_app()

if __name__ == "__main__":
    import os
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=debug, host="0.0.0.0", port=port)
