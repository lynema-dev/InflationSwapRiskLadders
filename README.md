# inflationswappricing
Pricing module for zero coupon inflation swaps in Python

A zero coupon inflation swap has one leg tied to a fixed rate and the other to a seasonally adjusted inflation series.  A net payment is made between an investor and a counterparty at maturity with not intermediate payments.  

This is a simple model which demonstrates the parts required and uses linear interpolation for computing discount factors and inflation curve projections.  No responsibility is taken for the accuracy of this model and is for demonstration purposes only.
