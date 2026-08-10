/*
 * ResumeAI Pro - Razorpay Payment
 * TEST MODE
 *
 * Flow:
 * 1. User clicks Choose Pro
 * 2. Guest -> login
 * 3. Logged-in user -> server creates Razorpay order
 * 4. Razorpay Checkout opens
 * 5. User can choose available payment methods
 * 6. Razorpay returns payment details
 * 7. Server verifies signature
 * 8. Pro plan activated
 */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {

        // ---------------------------------------------------------
        // ELEMENTS
        // ---------------------------------------------------------

        var section = document.querySelector('[data-logged-in]');

        var checkoutBtns =
            document.querySelectorAll('[data-start-checkout]');

        if (!checkoutBtns.length) {
            return;
        }

        var loggedIn = section
            ? section.getAttribute('data-logged-in') === 'true'
            : false;


        // ---------------------------------------------------------
        // CSRF TOKEN
        // ---------------------------------------------------------

        function getCsrf() {

            var meta =
                document.querySelector('meta[name="csrf-token"]');

            return meta
                ? meta.getAttribute('content')
                : '';
        }


        // ---------------------------------------------------------
        // MESSAGE
        // ---------------------------------------------------------

        function showMessage(message, type) {

            var msg =
                document.getElementById('payment-message');

            if (!msg) {

                msg = document.createElement('div');

                msg.id = 'payment-message';

                msg.className =
                    'alert alert-dismissible fade show mt-3';

                msg.innerHTML =
                    '<span class="payment-msg-text"></span>' +
                    '<button type="button" ' +
                    'class="btn-close" ' +
                    'data-bs-dismiss="alert"></button>';

                if (section) {
                    section.insertBefore(
                        msg,
                        section.firstChild
                    );
                }
            }

            msg.className =
                'alert alert-' +
                (type || 'danger') +
                ' alert-dismissible fade show mt-3';

            var text =
                msg.querySelector('.payment-msg-text');

            if (text) {
                text.textContent = message;
            }

            msg.classList.remove('d-none');
        }


        // ---------------------------------------------------------
        // CLEAR MESSAGE
        // ---------------------------------------------------------

        function clearMessage() {

            var msg =
                document.getElementById('payment-message');

            if (msg) {
                msg.classList.add('d-none');
            }
        }


        // ---------------------------------------------------------
        // POST JSON
        // ---------------------------------------------------------

        function postJson(url, payload) {

            return fetch(url, {

                method: 'POST',

                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrf(),
                    'X-Requested-With': 'XMLHttpRequest'
                },

                credentials: 'same-origin',

                body: JSON.stringify(payload || {})
            });
        }


        // ---------------------------------------------------------
        // CREATE RAZORPAY ORDER
        // ---------------------------------------------------------

        function createOrder(plan) {

            return postJson(
                '/payment/create-order',
                {
                    plan: plan
                }
            )
            .then(function (res) {

                if (
                    res.status === 401 ||
                    res.status === 403
                ) {

                    showMessage(
                        'Please login to continue with payment.',
                        'warning'
                    );

                    setTimeout(function () {

                        window.location.href =
                            '/auth/login?next=/pricing';

                    }, 800);

                    throw new Error(
                        'login required'
                    );
                }

                return res.json()
                    .then(function (data) {

                        if (!res.ok) {

                            throw new Error(
                                data.error ||
                                'Unable to create payment order.'
                            );
                        }

                        return data;
                    });
            });
        }


        // ---------------------------------------------------------
        // OPEN RAZORPAY CHECKOUT
        // ---------------------------------------------------------

        function openCheckout(orderData) {

            if (typeof Razorpay === 'undefined') {

                showMessage(
                    'Razorpay failed to load. Please refresh the page.',
                    'danger'
                );

                return;
            }


            /*
             * Razorpay Checkout
             *
             * UPI is requested as the preferred payment method.
             *
             * Depending on Razorpay account configuration,
             * device and TEST/LIVE environment, Razorpay may show:
             *
             * - UPI
             * - UPI ID
             * - QR / Scan & Pay
             * - Cards
             * - Netbanking
             * - Wallets
             *
             * IMPORTANT:
             * The JavaScript cannot force a QR scanner to appear
             * if Razorpay does not make that payment method available.
             */

            var options = {

                // -------------------------------------------------
                // RAZORPAY PUBLIC KEY
                // -------------------------------------------------

                key: orderData.key_id,

                // Amount comes from SERVER

                amount: orderData.amount,

                currency: orderData.currency,

                name: 'ResumeAI Pro',

                description:
                    orderData.plan.charAt(0).toUpperCase() +
                    orderData.plan.slice(1) +
                    ' Plan (TEST MODE)',

                order_id: orderData.order_id,


                // -------------------------------------------------
                // USER DETAILS
                // -------------------------------------------------

                prefill: {

                    name:
                        orderData.name || '',

                    email:
                        orderData.email || '',

                    contact:
                        orderData.phone || ''
                },


                // -------------------------------------------------
                // NOTES
                // -------------------------------------------------

                notes: {

                    plan:
                        orderData.plan,

                    payment_mode:
                        'UPI / QR / Card / Netbanking / Wallet'
                },


                // -------------------------------------------------
                // THEME
                // -------------------------------------------------

                theme: {

                    color: '#6c5ce7'
                },


                // -------------------------------------------------
                // PAYMENT METHOD DISPLAY
                // -------------------------------------------------

                config: {

                    display: {

                        blocks: {

                            upi_block: {

                                name: 'Pay using UPI',

                                instruments: [
                                    {
                                        method: 'upi'
                                    }
                                ]
                            }
                        },

                        sequence: [
                            'block.upi_block',
                            'card',
                            'netbanking',
                            'wallet'
                        ],

                        preferences: {

                            show_default_blocks: true
                        }
                    }
                },


                // -------------------------------------------------
                // SUCCESS
                // -------------------------------------------------

                handler: function (response) {

                    verifyPayment(
                        response,
                        orderData.plan
                    );
                },


                // -------------------------------------------------
                // MODAL
                // -------------------------------------------------

                modal: {

                    ondismiss: function () {

                        clearMessage();

                        showMessage(
                            'Payment cancelled. You can try again anytime.',
                            'warning'
                        );
                    }
                }
            };


            // -----------------------------------------------------
            // CREATE RAZORPAY INSTANCE
            // -----------------------------------------------------

            var rzp =
                new Razorpay(options);


            // -----------------------------------------------------
            // PAYMENT FAILED
            // -----------------------------------------------------

            rzp.on(
                'payment.failed',
                function (response) {

                    var errorMessage =
                        'Payment failed. Please try again.';

                    if (
                        response &&
                        response.error &&
                        response.error.description
                    ) {

                        errorMessage =
                            response.error.description;
                    }

                    showMessage(
                        'Payment failed: ' +
                        errorMessage,
                        'danger'
                    );
                }
            );


            // -----------------------------------------------------
            // OPEN CHECKOUT
            // -----------------------------------------------------

            rzp.open();
        }


        // ---------------------------------------------------------
        // VERIFY PAYMENT
        // ---------------------------------------------------------

        function verifyPayment(
            response,
            plan
        ) {

            clearMessage();

            if (
                !response ||
                !response.razorpay_payment_id ||
                !response.razorpay_order_id ||
                !response.razorpay_signature
            ) {

                showMessage(
                    'Payment details are incomplete.',
                    'danger'
                );

                return;
            }


            postJson(
                '/payment/verify',
                {

                    razorpay_payment_id:
                        response.razorpay_payment_id,

                    razorpay_order_id:
                        response.razorpay_order_id,

                    razorpay_signature:
                        response.razorpay_signature,

                    plan:
                        plan
                }
            )
            .then(function (res) {

                if (
                    res.redirected ||
                    res.type === 'opaqueredirect'
                ) {

                    window.location.href =
                        '/dashboard';

                    return;
                }


                return res.json()
                    .then(function (data) {

                        if (!res.ok) {

                            showMessage(
                                data.error ||
                                'Payment verification failed.',
                                'danger'
                            );

                            return;
                        }


                        showMessage(
                            'Your ' +
                            plan.charAt(0).toUpperCase() +
                            plan.slice(1) +
                            ' plan has been activated successfully!',
                            'success'
                        );


                        setTimeout(function () {

                            window.location.href =
                                '/dashboard';

                        }, 1000);
                    });
            })
            .catch(function (error) {

                console.error(
                    'Payment verification error:',
                    error
                );

                showMessage(
                    'Could not reach the server after payment. Please try again.',
                    'danger'
                );
            });
        }


        // ---------------------------------------------------------
        // START CHECKOUT
        // ---------------------------------------------------------

        function startCheckout(
            plan,
            btn,
            originalHtml
        ) {

            clearMessage();

            createOrder(plan)
                .then(function (orderData) {

                    if (btn) {

                        btn.disabled = false;

                        btn.innerHTML =
                            originalHtml;
                    }

                    openCheckout(orderData);
                })
                .catch(function (error) {

                    if (btn) {

                        btn.disabled = false;

                        btn.innerHTML =
                            originalHtml;
                    }

                    if (
                        error &&
                        error.message === 'login required'
                    ) {
                        return;
                    }

                    showMessage(
                        error.message ||
                        'Unable to start payment. Please try again.',
                        'danger'
                    );
                });
        }


        // ---------------------------------------------------------
        // GUEST -> SAVE PLAN -> LOGIN
        // ---------------------------------------------------------

        function storePlanThenLogin(plan) {

            postJson(
                '/payment/select-plan',
                {
                    plan: plan
                }
            )
            .then(function (res) {

                return res.json();
            })
            .then(function () {

                window.location.href =
                    '/auth/login?next=/pricing';
            })
            .catch(function (error) {

                console.error(
                    'Plan selection error:',
                    error
                );

                window.location.href =
                    '/auth/login?next=/pricing';
            });
        }


        // ---------------------------------------------------------
        // CHOOSE PRO / BUSINESS
        // ---------------------------------------------------------

        checkoutBtns.forEach(function (btn) {

            btn.addEventListener(
                'click',
                function () {

                    var plan =
                        btn.getAttribute(
                            'data-plan'
                        ) || 'pro';

                    clearMessage();


                    // ---------------------------------------------
                    // GUEST
                    // ---------------------------------------------

                    if (!loggedIn) {

                        storePlanThenLogin(plan);

                        return;
                    }


                    // ---------------------------------------------
                    // LOGGED IN
                    // ---------------------------------------------

                    var originalHtml =
                        btn.innerHTML;

                    btn.disabled = true;

                    btn.innerHTML =
                        '<i class="fas fa-spinner fa-spin me-2"></i>' +
                        'Processing...';


                    startCheckout(
                        plan,
                        btn,
                        originalHtml
                    );
                }
            );
        });


        // ---------------------------------------------------------
        // AUTO RESUME PENDING PLAN
        // ---------------------------------------------------------

        if (loggedIn) {

            postJson(
                '/payment/clear-plan',
                {}
            )
            .then(function (res) {

                return res.json();
            })
            .then(function (data) {

                var pending =
                    data.pending_plan;

                if (pending) {

                    startCheckout(
                        pending,
                        null,
                        ''
                    );
                }
            })
            .catch(function (error) {

                console.log(
                    'No pending payment plan.',
                    error
                );
            });
        }

    });

})();