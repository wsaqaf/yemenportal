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
  end
end
