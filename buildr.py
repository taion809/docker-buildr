from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

from docker import Client

app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('BUILDR_CONFIG', silent=True)

@app.route('/')
def show_index():
    return render_template('index.html')

@app.route('/payload', methods=['POST'])
def start_build():
    flash('Build started!')
    return redirect(url_for('show_index'))

if __name__ == '__main__':
    app.run('0.0.0.0')