# Use Apify's Python base image with Playwright
FROM apify/actor-python-playwright:3.11

# Copy all source files
COPY . ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Set the main script
CMD ["python", "-m", "main"]
