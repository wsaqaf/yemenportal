require "rails_helper"

describe MainPageController, type: :request do
  let(:user) { create(:user, role: "moderator") }
  let(:current_user) { create(:user, role: "admin") }

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
      let(:do_request) { get "/main_page?category=#{category.name}" }
      let(:do_bad_request) { get "/main_page?magic_name" }

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
end
