const ORDERS_API = 'http://192.168.90.3:5004';

function getOrders() {
    fetch(`${ORDERS_API}/api/orders`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        var tbody = document.querySelector('#order-list tbody');
        tbody.innerHTML = '';

        data.forEach(order => {
            var row = document.createElement('tr');

            // Id
            var idCell = document.createElement('td');
            idCell.textContent = order.id;
            row.appendChild(idCell);

            // User
            var userCell = document.createElement('td');
            userCell.textContent = order.user_name;
            row.appendChild(userCell);

            // Email
            var emailCell = document.createElement('td');
            emailCell.textContent = order.user_email;
            row.appendChild(emailCell);

            // Total
            var totalCell = document.createElement('td');
            totalCell.textContent = '$' + parseFloat(order.total).toFixed(2);
            row.appendChild(totalCell);

	    // Status
            var statusCell = document.createElement('td');
            statusCell.textContent = order.status;
            row.appendChild(statusCell);    
		

            // Date
            var dateCell = document.createElement('td');
            dateCell.textContent = new Date(order.created_at).toLocaleString();
            row.appendChild(dateCell);

            // Actions
            var actionsCell = document.createElement('td');
            var detailLink = document.createElement('a');
            detailLink.href = `/editOrder/${order.id}`;
            detailLink.textContent = 'View';
            detailLink.className = 'btn btn-info btn-sm';
            actionsCell.appendChild(detailLink);
            row.appendChild(actionsCell);

            tbody.appendChild(row);
        });
    })
    .catch(error => console.error('Error fetching orders:', error));
}

function getOrderDetail(orderId) {
    fetch(`${ORDERS_API}/api/orders/${orderId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) throw new Error('Order not found');
        return response.json();
    })
    .then(order => {
        document.getElementById('order-id').textContent = order.id;
        document.getElementById('order-user').textContent = order.user_name;
        document.getElementById('order-email').textContent = order.user_email;
        document.getElementById('order-total').textContent = parseFloat(order.total).toFixed(2);
	document.getElementById('order-status').textContent = order.status;    
        document.getElementById('order-date').textContent = new Date(order.created_at).toLocaleString();

        var tbody = document.getElementById('order-products');
        tbody.innerHTML = '';
        order.products.forEach(item => {
            var row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>$${parseFloat(item.unit_price).toFixed(2)}</td>
                <td>${item.quantity}</td>
                <td>$${parseFloat(item.subtotal).toFixed(2)}</td>
            `;
            tbody.appendChild(row);
        });
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error loading order details.');
    });
}

function updateOrderStatus(status) {

    const orderId = document.getElementById('order-id').textContent;

    const confirmationMessage =
        status === 'confirmed'
            ? '¿Está seguro de que desea confirmar esta orden?'
            : '¿Está seguro de que desea cancelar esta orden?';

    if (!confirm(confirmationMessage)) {
        return;
    }

    fetch(`${ORDERS_API}/api/orders/${orderId}/status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
            status: status
        })
    })

    .then(response => {

        return response.json().then(data => ({
            ok: response.ok,
            data: data
        }));

    })

    .then(result => {

        if (!result.ok) {
            throw new Error(result.data.message || 'Error updating status');
        }

        alert(result.data.message);

        getOrderDetail(orderId);
    })

    .catch(error => {
        console.error('Error updating order status:', error);
        alert(error.message);
    });
}
