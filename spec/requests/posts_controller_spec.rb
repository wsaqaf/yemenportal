require "rails_helper"

describe PostsController, type: :request do
  describe "#index" do
    let(:category) { create :category }

    context "without params" do
      let(:do_request) { get "/" }

      it "show a main page" do
        do_request

        expect(response).to have_http_status(:ok)
      end
    end

    context "with category params" do
      let(:do_request) { get "/posts?category=#{category.name}" }
      let(:do_bed_request) { get "/posts?magic_name" }

      it "show posts by category" do
        do_request

        expect(response).to have_http_status(:ok)
      end

      it "show a main page with incorrect params" do
        do_bed_request

        expect(response).to have_http_status(:ok)
      end
    end
  end

  describe "#update" do
    let(:post) { create :post }
    let(:category) { create :category }
    let(:headers) { { "HTTP_REFERER" => "some_place" } }
    let(:do_request) { put "/posts/#{post.id}", headers: headers, params: { state: "aprouved" } }
    let(:update_categories) { put "/posts/#{post.id}", params: { category_ids: [category.id] } }

    it "change category list" do
      update_categories

      expect(response).to have_http_status(200)
    end

    it "change post state" do
      do_request

      expect(response).to have_http_status(302)
      expect(response).to redirect_to("some_place")
    end
  end
end
