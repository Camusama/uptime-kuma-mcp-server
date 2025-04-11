import pytest
import subprocess
import sys
import time
from uptime_kuma_mcp_server import run_sse

def test_sse_server_starts():
    """Test if SSE server can start successfully"""
    try:
        # Use current interpreter path to start service
        process = subprocess.Popen(
            [sys.executable, "-c", "from uptime_kuma_mcp_server import run_sse; run_sse()"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for service to start
        time.sleep(2)
        
        # Check if process is still running
        assert process.poll() is None, "SSE server process has exited"
        
        # Terminate process after test
        process.terminate()
        process.wait()
    except Exception as e:
        pytest.fail(f"SSE server start test failed: {str(e)}")