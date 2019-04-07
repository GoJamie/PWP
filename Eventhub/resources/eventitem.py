from flask_restful import Resource


class EventItem(Resource):

    def get(self, handle):
        db_product = Product.query.filter_by(handle=handle).first()
        if db_product is None:
            return create_error_response(404, "Not found",
                                         "No product was found with the handle {}".format(
                                             handle)
                                         )

        body = InventoryBuilder(
            id=EventItem.id,
            weight=db_product.weight,
            price=db_product.price

        )
        body.add_namespace("prohub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(ProductItem, handle=handle))
        body.add_control("profile", PRODUCT_PROFILE)
        body.add_control_delete_event(handle)
        body.add_control_edit_event(handle)
        body.add_control_all_event()

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, handle):
        return
