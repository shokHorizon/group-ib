import socket
import string
import threading

import homoglyphs as hg


def ping_list(domain_iter: iter, zones: list):
    while(True):
        try:
            prepared_domain = next(domain_iter)
            domains = list(map(lambda zone: f'{prepared_domain}.{zone}', zones))

            for domain in domains:
                try:
                    res = socket.gethostbyname(domain)
                    print(f'{domain} - {res}')

                except socket.gaierror:
                    continue
                except KeyboardInterrupt:
                    break
        except StopIteration:
            break
    return 


def main(domains: list, zones: list):
    homoglyphs = hg.Homoglyphs(categories=('LATIN', 'COMMON'), strategy=hg.STRATEGY_LOAD, ascii_strategy=hg.STRATEGY_LOAD)

    last_symbol_domains = set()
    homoglyph_domains = set()
    additional_dot_domains = set()
    symbol_remove_domains = set()

    for domain in domains:
        if len(domain) > 2:
            for i in range(1, len(domain)-1):
                if domain[i-1] != '-' and domain[i+1] != '-':
                    additional_dot_domains.add(f'{domain[0:i]}.{domain[i:-1]}')

        last_symbol_domains.update(list(map(lambda char: domain+char, string.digits + string.ascii_letters)))

        for i in range(len(domain)):
            char_combinations = homoglyphs.get_combinations(domain[i])
            if i == 0:
                homoglyph_domains.update((char + domain[1:] for char in char_combinations))
            elif i == len(domain) - 1:
                homoglyph_domains.update((domain[:-1] + char for char in char_combinations))
            else:
                homoglyph_domains.update((domain[:i] + char + domain[i+1:] for char in char_combinations))

            if domain[i] == '-' and i in (0, len(domain)-1):
                continue
            symbol_remove_domains.add(f'{domain[0:i]}{domain[i+1:]}')

    homoglyph_domains -= set(domain)
            

    domains_to_chech = last_symbol_domains | homoglyph_domains | additional_dot_domains | symbol_remove_domains
    prepared_domains_iter = iter(domains_to_chech)
    workers = list()

    #Запуск оптимального количества потоков
    while(not workers or len(domains_to_chech)//len(workers) > 16 and len(workers) < 32):
        t = threading.Thread(target=ping_list, args=[prepared_domains_iter, zones])
        t.start()
        workers.append(t)

    for worker in workers:
        try:
            worker.join()
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    domains = list()
    zones = 'com, ru, net, org, info, cn, es, top, au, pl, it, uk, tk, ml, ga, cf, us, xyz, top, site, win, bid'.split(', ')

    while(len(domains) == 0):
        try:
            raw_domains = input('Введите домены через запятую и пробел (group-ib):') or 'group-ib'
            raw_domains = raw_domains.strip().split(', ')
                
            for domain in raw_domains:
                domain = domain.replace('-', '')
                if not domain.isalnum():
                    raise ValueError

            domains.extend(raw_domains)
        except ValueError:
            print('Проверьте правильность ввода')
        except KeyboardInterrupt:
            break

    main(raw_domains, zones)
