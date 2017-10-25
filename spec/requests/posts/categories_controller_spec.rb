require "rails_helper"

describe Posts::CategoriesController, type: :request do
  describe "PUT #update" do
    let(:post_id) { 1 }
    let(:params) { {} }
    let(:do_request) { put "/posts/#{post_id}/categories", params: params }

    context "when user is unauthorized" do
      it "returns redirect code" do
        do_request
        expect(response.status).to eq(302)
      end
    end

    context "when user has no permission to update post" do
      include_context "authenticated user"

      it "returns unauthorized code" do
        do_request
        expect(response).to have_http_status(:unauthorized)
      end
    end

    context "when user has permission to update post" do
      include_context "authenticated user" do
        let(:current_user_role) { "moderator" }
      end

      context "when there is no post for request" do
        let(:post_id) { 404 }

        it "returns 404 code" do
          expect { do_request }.to raise_error(ActiveRecord::RecordNotFound)
        end
      end

      context "when there is a post for request" do
        let(:categories) { create_list(:category, 2) }
        let(:category_names) { categories.map(&:name).join(", ") }
        let(:params) { { category_ids: categories.map(&:id) } }
        let(:post) { create(:post) }
        let(:post_id) { post.id }

        it "return 200 code" do
          do_request
          expect(response).to have_http_status(:ok)
        end

        it "returns updated post category names" do
          do_request
          expect(JSON.parse(response.body))
            .to match("category_names" => category_names)
        end
      end
    end
  end
end
