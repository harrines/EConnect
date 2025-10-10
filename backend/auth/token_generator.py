from auth_handler import signJWT

# Generate token for admin
admin_token = signJWT("admin_id", "admin")

# Generate token for user
user_token = signJWT("user_id", "user")

# Print the generated tokens (you can store them in a file or database as needed)
print("Admin Token:", admin_token)
print("User Token:", user_token)



