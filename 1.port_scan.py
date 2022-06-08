import ipaddress
import threading
import socket
import requests


def ping_list(ip_iter, port_list: list)-> dict:
    dict_ip_to_ports = dict()

    while(True):
        try:
            ipv4 = str(next(ip_iter))
            for port in port_list:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        s.connect((ipv4, port))
                        if ipv4 not in dict_ip_to_ports:
                            dict_ip_to_ports[ipv4] = list()
                        dict_ip_to_ports[ipv4].append(port)
                        print(f'{ipv4} {port} OPEN')

                        res = None

                        match(port):
                            case 443:
                                res = requests.get('https://' + ipv4, verify=False)
                            case 80:
                                res = requests.get('http://' + ipv4)
                            case _:
                                continue
                            
                        name = res.headers.get('server')

                        if name:
                            print(f'{ipv4} - {name}')

                except TimeoutError:
                    continue
                except KeyboardInterrupt:
                    break
        except StopIteration or KeyboardInterrupt:
            break

    return dict_ip_to_ports


def main(net_address: ipaddress.ip_network, ports: list):
    address_range = list(net_address.hosts())
    address_iter = iter(address_range)

    workers = list()

    #Запуск оптимального количества потоков
    while(not workers or len(address_range)//len(workers) > 16 and len(workers) < 16):
        t = threading.Thread(target=ping_list, args=[address_iter, ports])
        t.start()
        workers.append(t)

    for worker in workers:
        worker.join()


if __name__ == '__main__':
    #Отключение предупреждений о неиспользовании сертификатов ssl
    requests.packages.urllib3.disable_warnings()

    net_address = None
    ports = list()

    while(net_address is None):
        try:
            net_address = ipaddress.ip_network(
                input('Введите адрес (192.168.0.1/24):') or '192.168.0.1/24',
                False
                )
            if net_address.prefixlen == 32:
                net_address = None
                raise ValueError
        except ValueError:
            print('Введите корректный адрес')

    while(len(ports) == 0):
        raw_ports = input('Введите порты через запятую и пробел(80, 443):') or '80, 443'
        try:
            raw_ports = list(map(int, raw_ports.strip().split(', ')))
            ports.extend(raw_ports)
        except TypeError:
            print('Проверьте корректность ввода')

    main(net_address, ports)
