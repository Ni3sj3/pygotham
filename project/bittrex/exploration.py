from bittrex import Bittrex

"""
From the API documentation ()
"We are currently restricting orders to 500 open orders and 200,000 orders a day.
We reserve the right to change these settings as we tune the system.
If you are affected by these limits as an active trader,
please email support@bittrex.com."

"""
bt = Bittrex(None, None)


test = True


if test:
    DEPTH_TYPES = ['buy', 'sell', 'both'] # sell is not ask, as one might assume...

    btc_eth = 'BTC-ETH'
    eth_ltc = 'ETH-LTC'
    btc_ltc = 'BTC-LTC'

    test_triangle = (btc_eth, eth_ltc, btc_ltc)
    test_markets  = [Market(m) for m in test_triangle]
    test_cycle    = Cycle(test_markets)

    # we implemented __getitem__ for Cycle so that we should be able to iterate over the test_cycle.  Let's test that!
    print ('\nTest Cycle')
    for idx, (market, order_type) in enumerate(test_cycle):
        print('\t({}) {} => {}'.format(idx, market, order_type))

    fee = 0.25/100 # 0.25% commission

    
    


class Market:
    def __init__(self, name):
        self.base, self.to = name.split('-')

    def __eq__(self, oth):
        return self.base == oth.base and self.to == oth.to

    def __str__(self):
        return '{}-{}'.format(self.base, self.to)

    def __repr__(self):
        return  'Market (base: {}, to: {})'.format(self.base, self.to)


    
class Cycle:
    
    def __init__(self, markets):
        if len(markets) < 3 or (markets[0].base != markets[-1].to
                                    and markets[0].base != markets[-1].base):
            raise ValueError

        self.markets = markets
        
        self.start = markets[0]
        self.end   = markets[-1]

        self.order_types = ['buy'] # will assume the first is always a buy, WLOG

        for prev_market, cur_market in zip(markets, markets[1:]):

            prev_currency = (
                prev_market.to if self.order_types[-1] == 'buy'
                else prev_market.base
                )
                
            if cur_market.base == prev_currency:
                self.order_types.append('buy')
            elif cur_market.to == prev_currency:
                self.order_types.append('sell')
            else:
                raise ValueError('Invalid market sequence {} {} w/ prev trade {}'
                                     .format(prev_market, cur_market,
                                                 self.order_types[-1]) )
                    

        assert(len(self.markets) == len(self.order_types))


    def __getitem__(self, index):
        return (self.markets[index], self.order_types[index])
    
    
    def __str__(self):
        return ' \tMARKETS:\t\t{}\n\tORDER TYPES:\t{}'.format(self.markets, self.order_types)

    
    def __repr__(self):
        return 'Cycle\n{}'.format(self.__str__())


    
class CycleArbitrage:
    def __init__(self, cycle, fee=0.00025, wiggle=0):
        self.cycle  = cycle
        self.fee    = fee
        self.wiggle = wiggle


    def __str__(self):
        return 'Cycle: {}\nFee Fraction: {}\nWiggle: {}'.format(
            self.cycle,
            self.fee,
            self.wiggle
            )

    def __repr__(self):
        return 'CycleArbitrage: {}'.format(self.__str__())


    def round_trip(self):
        
        prod = 1.0


    
    

def get_markets():
    response = bt.get_markets()

    markets = (
        [ info['MarketName'] for info in response['result'] ]
        if response['success']
        else None
    )
    
    return markets


def get_currencies():
    response = bt.get_currencies()

    currencies = (
        response['result']
        if response['success']
        else None
        )

    return currencies

def get_buys(market):
    response = bt.get_orderbook(market, 'buy', depth=10)

    buys = response['result'] if response['success'] else None

    return buys


def get_asks(market):
    response = bt.get_orderbook(market, 'sell', depth=10)

    asks = response['result'] if response['success'] else None
    return asks


def test_asks(market):
    asks = get_asks(market)

    print('Got {} asks back'.format(len(asks)))
    
    if all(cur['Rate'] <= next['Rate'] for cur, next in zip(asks, asks[1:])):
        print('Asks order book is weakly increasing')
    else:
        print('Something\'s wrong -- Asks order book is not weakly increasing')
    

def test_buys(market):
    buys = get_buys(market)

    print('Got {} buys back'.format(len(buys)))
    
    if all(cur['Rate'] >= next['Rate'] for cur, next in zip(buys, buys[1:])):
        print('Buys order book is weakly decreasing')
    else:
        print('Something\'s wrong -- Buys order book is not weakly decreasing')
    

if __name__ == '__main__':
    pass



