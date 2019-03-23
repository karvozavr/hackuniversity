import datetime

from database import Database
from solution.heap import Heap


class Equipment:
    def __init__(self, id, clazz, available_hours, speed_per_hour, available_time):
        self.id = id
        self.clazz = clazz
        self.available_hours = available_hours
        self.speed_per_hour = speed_per_hour
        self.available_time = available_time

    def __lt__(self, other):
        return False


class Order:
    def __init__(self, id, product_id, amount, deadline, equipment):
        self.id = id
        self.product_id = product_id
        self.amount = amount
        self.deadline = deadline
        self.equipment = equipment


def to_equipment(eq, start_time):
    return Equipment(id=eq[0], clazz=eq[1], available_hours=eq[2], speed_per_hour=int(eq[3]), available_time=start_time)


def to_order(order):
    return Order(id=order[0], product_id=order[1], amount=int(order[2]), deadline=float(order[3]), equipment=order[4])


class KTetris:
    def __init__(self, db, k=10, step_size=1000, start_timestamp=1552867200, callback=print):
        self.db = db
        self.k = k
        self.step_size = step_size
        self.start_timestamp = start_timestamp
        self.heaps = self.build_equipment_heaps()
        self.n = 0
        self.callback = callback
        self.total = 0
        self.finished = 0

    def performance(self):
        return self.finished / self.total

    def get_key_by_equipment(self, eq):
        return eq.available_time + (self.k / eq.speed_per_hour) * 60 * 60

    def build_equipment_heaps(self):
        equipment_classes = self.db.execute('SELECT DISTINCT(equipment_class) FROM equipment;')
        if equipment_classes is None:
            raise Exception('Unable to access equipment.')

        heaps = {}
        for eq_class, in equipment_classes:
            all_in_class = list(map(lambda x: to_equipment(x, self.start_timestamp),
                                    self.db.execute(
                                        f'SELECT * FROM equipment WHERE equipment_class = \'{eq_class}\';')))
            heaps[eq_class] = Heap(initial=all_in_class,
                                   key=(lambda x: self.get_key_by_equipment(x)))

        return heaps

    def get_orders(self, offset: int, limit: int):
        orders = map(to_order, self.db.execute(
            'SELECT O.id AS order_id, product_id, amount, EXTRACT(epoch FROM deadline) as deadline, equipment_class '
            'FROM "order" AS O '
            'LEFT JOIN product as P '
            'ON (O.product_id = P.id) '
            'ORDER BY O.deadline '
            f'OFFSET {offset} '
            f'LIMIT {limit};'))
        if orders is None:
            raise Exception('Unable to access orders.')
        return orders

    def solve(self):
        size = self.db.execute('SELECT COUNT(*) FROM "order";')
        if size is None:
            raise Exception('Unable to access orders.')

        if size[0][0] <= 0:
            raise Exception('No orders in table.')

        self.total = size[0][0]

        for iteration in range((size[0][0] + (self.step_size - 1)) // self.step_size):
            offset = iteration * self.step_size
            orders = self.get_orders(offset, self.step_size)
            yield self.update_solution_with_batch(orders)

    def update_solution_with_batch(self, orders):
        for order in orders:
            yield self.update_solution_with_order(order)

    def update_solution_with_order(self, order):
        queue = []

        equipment = list(filter(lambda x: x in self.heaps.keys(), map(lambda x: x, order.equipment)))

        while order.amount > 0:
            self.push_best_equipment(equipment, queue, order)

        for eq, time, _, _ in queue:
            if eq.available_time + time >= order.deadline:
                for eq2, _, heap, _ in queue:
                    heap.push(eq2)
                return

        for eq2, t, heap, amount in queue:
            yield self.export_result(eq2, order, amount, t)
            eq2.available_time += t
            heap.push(eq2)

    def export_result(self, eq, order, amount, work_time):
        self.finished += 1
        data = {'id': self.n,
                'equipment_id': eq.id,
                'order_id': order.id,
                'amount': amount,
                'start_time': eq.available_time,
                'finish_time': eq.available_time + work_time}
        yield data

    def push_best_equipment(self, equipment, queue, order):
        min_heap = None
        best_value = float('inf')

        for eq_class in equipment:
            heap = self.heaps[eq_class]
            if heap.empty():
                continue
            eq = heap.top()
            key = self.get_key_by_equipment(eq)
            if key < best_value:
                best_value = key
                min_heap = heap

        if min_heap is not None:
            min_eq = min_heap.top()
        else:
            min_eq = None

        is_so = False

        for eq, _, heap, _ in queue:
            key = self.get_key_by_equipment(eq)
            if key < best_value:
                best_value = key
                min_eq = eq
                min_heap = heap
                is_so = True

        min_eq = min_heap.pop() if not is_so else min_eq

        work_time = self.increment_available_time(min_eq, order)

        order.amount -= min(order.amount, self.k)

        queue.append((min_eq, work_time, min_heap, min(order.amount, self.k)))

    @staticmethod
    def next_weekday(d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return d + datetime.timedelta(days_ahead)

    def increment_available_time(self, eq, order):
        work_time = ((min(order.amount, self.k)) / eq.speed_per_hour) * 60 * 60

        start_time = datetime.datetime.fromtimestamp(eq.available_time)
        end_time = start_time + datetime.timedelta(seconds=work_time)

        weekend_begin = self.next_weekday(start_time, 5)

        if end_time > weekend_begin:
            work_time += datetime.timedelta(days=2).seconds

        return work_time


if __name__ == '__main__':
    k_tetris = KTetris(Database(), k=700, callback=(lambda x: None))
    l = list(k_tetris.solve())
    print(l)
