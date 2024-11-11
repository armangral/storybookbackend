import asyncio
import getpass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.core.security import gen_new_key
from app.models.user import User


# Utility to prompt for user input asynchronously
async def prompt_input(prompt_text: str):
    return input(prompt_text)


# Utility to handle password prompts and validation
async def prompt_password():
    while True:
        password = getpass.getpass("Enter password (at least 8 characters): ")
        if len(password) < 8:
            print("Password must be at least 8 characters long. Try again.")
            continue
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Passwords do not match. Try again.")
            continue
        return password


# Function to create admin user
async def create_admin_user(db: AsyncSession):
    email = await prompt_input("Enter admin email: ")

    # Prompt for password and confirm password
    password = await prompt_password()

    # Hash the password and generate salt (you can adapt this based on your security implementation)
    hashed_password, password_salt = gen_new_key(password)

    # Create user entry in the User table
    new_user = User(
        first_name = "super",
        last_name = "admin",
        username=email,
        password=hashed_password,
        password_salt=password_salt,
        is_super_admin=True,
    )
    db.add(new_user)
    await db.flush()  # Ensure the user ID is generated for use in the admin table


    # Commit the transaction
    await db.commit()
    print("super admin created successfully.")


# Main entry point for the script
async def main():
    async with SessionLocal() as session:  # Assuming async_session is a factory for AsyncSession
        async with session.begin():
            await create_admin_user(session)


# Run the script
if __name__ == "__main__":
    asyncio.run(main())
