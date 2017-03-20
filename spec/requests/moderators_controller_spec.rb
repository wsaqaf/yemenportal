require "rails_helper"

describe ModeratorsController, type: :request do
  describe "#destroy" do
    let(:user) { create(:user, role: "moderator") }
    let(:do_request) { delete "/moderators/#{user.id}", headers: { "HTTP_REFERER" => "some_path" } }

    it "change moderator role" do
      do_request

      expect(response).to redirect_to("some_path")
    end
  end

  describe "#index" do
    let(:do_request) { get "/moderators" }

    it "redirect to sources list" do
      do_request

      expect(response.status).to eq 200
    end
  end
end
