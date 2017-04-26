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
      let(:user) { build :user }
      let(:do_request) { get "/posts?category=#{category.name}" }
      let(:do_bad_request) { get "/posts?magic_name" }

      it "show posts by category" do
        do_request

        expect(response).to have_http_status(:ok)
      end

      it "show posts by category for authorization" do
        sign_in user
        do_request

        expect(response).to have_http_status(:ok)
      end

      it "show a main page with incorrect params" do
        do_bad_request

        expect(response).to have_http_status(:ok)
      end
    end
  end

  describe "#update" do
    let(:category) { create :category }
    let(:post) { create :post, state: "pending" }
    let(:headers) { { "HTTP_REFERER" => "some_place" } }
    let(:post) { create :post, state: "pending" }
    let(:do_request) { put "/posts/#{post.id}", headers: headers, params: { state: "approved" } }
    let(:update_categories) { put "/posts/#{post.id}", params: { category_ids: [category.id] } }

    it "change category list" do
      update_categories

      expect(response).to have_http_status(200)
    end

    it "return 302 state and redirrect to back" do
      expect { do_request }.to change { Post.approved_posts.count }

      expect(Post.find(post.id).state).to eql("approved")
      expect(response).to have_http_status(302)
      expect(response).to redirect_to("some_place")
    end
  end
end
