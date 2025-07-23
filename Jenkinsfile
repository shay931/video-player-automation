pipeline {
    agent any
    environment {
        PROJECT_DIR = "${WORKSPACE}"
        PROJECT_ROOT = "${WORKSPACE}"
        PYTHONUNBUFFERED = "1"  // Force Python to flush output immediately
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
        stage('Create Report Directories') {
            steps {
                bat """
                cd %PROJECT_DIR%
                if not exist reports mkdir reports
                if not exist reports\\logs mkdir reports\\logs
                if not exist reports\\screenshots mkdir reports\\screenshots
                echo "Created report directories"
                dir reports
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
                set PROJECT_ROOT=%PROJECT_ROOT%
                set PYTEST_CURRENT_TEST=api_tests
                echo "Running API tests..."
                call pytest tests/test_api_positive.py tests/test_api_negative.py -v -s --html=reports/report_api.html --junitxml=reports/results_api.xml --log-cli-level=INFO
                echo "API tests completed"
                """
            }
        }
        stage('Run Parallel Tests') {
            steps {
                bat """
                cd %PROJECT_DIR%
                call venv\\Scripts\\activate.bat
                set PROJECT_ROOT=%PROJECT_ROOT%
                set PYTEST_CURRENT_TEST=video_tests
                call pip install pytest-xdist
                echo "Running Video tests..."
                call pytest tests/test_video.py -v -s --html=reports/report_video.html --junitxml=reports/results_video.xml --log-cli-level=INFO
                echo "Video tests completed"
                """
            }
        }
        stage('List Report Files') {
            steps {
                bat """
                cd %PROJECT_DIR%
                echo "=== Listing all report files ==="
                echo "Reports directory:"
                dir reports /s /b
                echo "=== Log files ==="
                dir reports\\logs\\*.log
                echo "=== Screenshot files ==="
                dir reports\\screenshots\\*.png
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
            // Archive all artifacts from reports directory
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
            
            // Also archive from root if any
            archiveArtifacts artifacts: '*.html, *.xml', allowEmptyArchive: true
            
            // JUnit results
            junit allowEmptyResults: true, testResults: 'reports/results_*.xml'
            
            // HTML Publisher for reports
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'report_api.html, report_video.html',
                reportName: 'Test Reports'
            ])
        }
        success {
            echo 'Tests passed successfully!'
        }
        failure {
            echo 'Tests failed! Check the reports and logs.'
        }
    }
}