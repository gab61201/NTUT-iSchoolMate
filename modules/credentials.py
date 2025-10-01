import keyring
import logging

class CredentialsManager:
    """
    用以安全地儲存使用者的密碼在本地
    """
    # 定義一個獨特的服務名稱，用來在系統中識別您的應用程式
    SERVICE_NAME = 'NTUT-iSchool-Pro'

    def save(self, username: str, password: str) -> None:
        """
        將密碼安全地儲存到作業系統的鑰匙圈中。
        """
        try:
            keyring.set_password(self.SERVICE_NAME, username, password)
            logging.info(f"已為使用者 '{username}' 安全地儲存憑證。")
        except Exception as e:
            logging.error(f"儲存憑證時發生錯誤: {e}")

    def load(self, username: str) -> str | None:
        """
        從作業系統的鑰匙圈中讀取密碼。
        """
        try:
            password = keyring.get_password(self.SERVICE_NAME, username)
            if password:
                logging.info(f"已成功為使用者 '{username}' 載入憑證。")
                return password
            else:
                logging.warning(f"在鑰匙圈中找不到使用者 '{username}' 的憑證。")
                return None
        except Exception as e:
            logging.error(f"載入憑證時發生錯誤: {e}")
            return None

    def delete(self, username: str) -> None:
        """
        從作業系統的鑰匙圈中刪除密碼。
        """
        try:
            keyring.delete_password(self.SERVICE_NAME, username)
            logging.info(f"已為使用者 '{username}' 刪除憑證。")
        except Exception as e:
            logging.error(f"刪除憑證時發生錯誤: {e}")

if __name__ == "__main__":
    cred_manager = CredentialsManager()
    cred_manager.delete('b11011001')
    saved_password = cred_manager.load('b11011001')
    print(saved_password)