pipeline {
    agent any

    environment {
        PROJECT_DIR = "${WORKSPACE}"
        PROJECT_ROOT = "${WORKSPACE}"  // ← לפייתון
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

        stage('Run Regular Tests') {
            steps {
                bat """
                cd %PROJECT_DIR%
                call venv\\Scripts\\activate.bat
                call pytest tests/test_api_positive.py tests/test_api_negative.py --html=report_api.html --junitxml=results_api.xml
                """
            }
        }

        stage('Run Parallel Tests') {
            steps {
                bat """
                cd %PROJECT_DIR%
                call venv\\Scripts\\activate.bat
                call pip install pytest-xdist
                call pytest tests/test_video.py -n auto --html=report_video.html --junitxml=results_video.xml
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
            archiveArtifacts artifacts: '*.html, *.xml', allowEmptyArchive: false
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true  // ← הוספה כאן
            junit 'results_*.xml'
        }
    }
}
