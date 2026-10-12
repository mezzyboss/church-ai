# church-ai
automation for church activities

## StreamYard Playwright proof of concept

This proof of concept opens StreamYard in Microsoft Edge using an existing Edge
profile. It does not create a stream.

1. Install Python 3.9 or newer and Microsoft Edge.
2. Install the project dependency:

   ```sh
   python -m pip install -r requirements.txt
   ```

3. Find the Edge user data directory. In Edge, open `edge://version` and look
   for **Profile path**. Use its parent directory as the user data directory
   (for example, use `.../User Data`, not `.../User Data/Default`).
4. Close all Edge windows that use that profile so Playwright can open it.
5. Set `STREAMYARD_EDGE_USER_DATA_DIR` to the directory from step 3, then run:

   ```sh
   python scripts/streamyard_poc.py
   ```

   Alternatively, pass the directory with `--user-data-dir`.

The script logs its progress, leaves the opened page available for interaction,
and closes Edge when you press Enter or Ctrl+C. The selected profile must
already be signed in to StreamYard for the authenticated session to be reused.
The profile contains browser data and should not be copied into or committed to
this repository.
