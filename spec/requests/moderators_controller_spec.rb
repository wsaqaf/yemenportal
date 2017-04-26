require "rails_helper"

describe ModeratorsController, type: :request do
  let(:user) { create(:user, role: "moderator") }
  let(:current_user) { create(:user, role: "admin") }

  describe "#destroy" do
    let(:user) { create(:user, role: "moderator") }
    let(:do_request) { delete "/moderators/#{user.id}", headers: { "HTTP_REFERER" => "some_path" } }

    it "change moderator role" do
      sign_in current_user
      do_request

      expect(response).to redirect_to("some_path")
    end
  end

  describe "#index" do
    let(:do_request) { get "/moderators" }

    it "redirect to sources list" do
      sign_in current_user
      do_request

      expect(response.status).to eq 200
    end
  end
end
