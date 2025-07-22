pipeline {
    agent any

    environment {
        PROJECT_DIR = "${WORKSPACE}"
    }

    stages {
        stage('Setup Python Env') {
            steps {
                bat """
                cd %PROJECT_DIR%
                python -m venv venv
                call venv\\Scripts\\activate.bat
                call python -m pip install --upgrade pip
                call pip install -r requirements.txt
                """
            }
        }

        stage('Install Node Modules') {
            steps {
                bat """
                cd %PROJECT_DIR%\\server
                call npm install
                """
            }
        }

        stage('Start Backend Server') {
            steps {
                bat """
                cd %PROJECT_DIR%\\server
                start "" cmd /c "npm start"
                ping 127.0.0.1 -n 6 > nul
                """
            }
        }

        stage('Run Tests') {
            steps {
                bat """
                cd %PROJECT_DIR%
                call venv\\Scripts\\activate.bat
                call pytest tests/ --html=report.html --junitxml=results.xml
                """
            }
        }

        stage('Stop Backend Server') {
            steps {
                bat 'taskkill /F /IM node.exe || exit 0'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'report.html', allowEmptyArchive: false
            junit 'results.xml'

            publishHTML(target: [
                reportDir: '.',
                reportFiles: 'report.html',
                reportName: 'HTML Report'
            ])
        }
    }
}
