import psycopg2
import glob
import time
from dotenv import load_dotenv
import os

#.env
load_dotenv()

db_name = os.getenv('DB_NAME')
db_password = os.getenv('DB_PASSWORD')
queue_id = os.getenv('QUEUE_ID')
user_id = os.getenv('USER_ID')

while True:
    try:
        env_files = glob.glob('/opt/*/Bot/backend/.env')
        env_file_path = env_files[0]

        with open(env_file_path, 'r') as file:
            for line in file:
                if 'NAMECHAT=' in line:
                    namechat_value = line.split('=')[1].strip()
                    break
            else:
                print("Linha NAMECHAT não encontrada no arquivo")


        conn = psycopg2.connect(
            dbname=f"{namechat_value}",
            user=f"{db_name}",
            password=f"{db_password}",
            host="172.17.0.1"
        )


        cur = conn.cursor()
        cur.execute("""
        
                        SELECT id, status  
                        FROM tickets t 
                        WHERE status = 'in_bot' 
                        AND queue_id IS NOT NULL 
                        AND closed_at IS NOT NULL;
        
        """)
        rows = cur.fetchall()
        print(rows)

        if len(rows) >= 1:
            print('Existe ticket  preso na automação')

            for row in rows:
                ticket_id = row[0]

                

                cur.execute(f"""
                            UPDATE tickets
                            SET status = 'close'
                            WHERE id = {ticket_id}
                
                """)
                print(f'Ticket {ticket_id} foi encerrado')
                conn.commit()

        #Busca os atendimentos que está em automação a pelo menos 35min
        cur.execute("""
                        FROM tickets t 
                        WHERE status = 'in_bot' 
                        AND queue_id IS NULL 
                        AND closed_at IS NULL 
                        AND created_at <= NOW() - INTERVAL '35 MINUTES';
        
        """)

        rows = cur.fetchall()
        print(rows)

        if len(rows) >= 1:
            print('Existe ticket  preso na automação')

            for row in rows:
                ticket_id = row[0]

                

                cur.execute(f"""
                            update tickets set status = 'open', queue_id = {queue_id}, user_id = {user_id} where id = {ticket_id}
                """)
                print(f'Ticket {ticket_id} foi transferido')
                conn.commit()
        else: 
            print('Não existe ticket preso na automação')

        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print("Erro ao conectar ao banco de dados")
        print(e)


    time.sleep(1 * 60)