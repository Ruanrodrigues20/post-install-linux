import subprocess
import sys

def run_cmd(cmd, cwd=None, sudo=False, check=False, capture_output=False, senha=None):
    if sudo:
        if senha is None:
            raise ValueError("⚠️ Você deve fornecer a senha quando sudo=True.")
        full_cmd = ['sudo', '-S'] + cmd
    else:
        full_cmd = cmd

    try:
        if capture_output:
            result = subprocess.run(
                full_cmd,
                cwd=cwd,
                input=(senha + '\n') if sudo else None,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=check
            )
            return result
        else:
            proc = subprocess.Popen(
                full_cmd,
                cwd=cwd,
                stdin=subprocess.PIPE if sudo else None,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )
            if sudo:
                proc.stdin.write(senha + '\n')
                proc.stdin.flush()
            proc.wait()
            if check and proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode, cmd)
            return proc
    except Exception as e:
        print(f"❌ Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(f"Detalhe: {e}", file=sys.stderr)
        sys.exit(1)


run_cmd(["apt","update"], sudo=True, senha="0607")