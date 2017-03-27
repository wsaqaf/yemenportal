# == Schema Information
#
# Table name: users
#
#  id                     :integer          not null, primary key
#  email                  :string           default(""), not null
#  first_name             :string
#  last_name              :string
#  created_at             :datetime         not null
#  updated_at             :datetime         not null
#  role                   :enum             default("MEMBER"), not null
#  encrypted_password     :string           default(""), not null
#  reset_password_token   :string
#  reset_password_sent_at :datetime
#  remember_created_at    :datetime
#  sign_in_count          :integer          default("0"), not null
#  current_sign_in_at     :datetime
#  last_sign_in_at        :datetime
#  current_sign_in_ip     :inet
#  last_sign_in_ip        :inet
#  confirmation_token     :string
#  confirmed_at           :datetime
#  confirmation_sent_at   :datetime
#  unconfirmed_email      :string
#
# Indexes
#
#  index_users_on_email                 (email) UNIQUE
#  index_users_on_reset_password_token  (reset_password_token) UNIQUE
#

require "rails_helper"

describe User do
  %i(email role).each do |field|
    it { is_expected.to validate_presence_of(field) }
  end

  describe "#from_omniauth" do
    let(:user) { build(:user, email: "aa@aa.aa") }
    let(:info) { double(email: "aa@aa.aa") }
    let(:auth) { double(:auth, provider: "twitter", uid: "some_uid", info: info) }

    context "New identity object" do
      let(:identity) { build(:identity) }

      it "find user" do
        allow(described_class).to receive(:new).and_return(user)
        allow(user).to receive(:persisted?).and_return(false)
        expect(Identity).to receive(:create).with(provider: "twitter", uid: "some_uid", user: user).and_return(identity)
        described_class.from_omniauth(auth)
      end

      it "create user" do
        allow(described_class).to receive(:new).and_return(user)
        expect(Identity).to receive(:create).with(provider: "twitter", uid: "some_uid", user: user).and_return(identity)
        described_class.from_omniauth(auth)
      end
    end

    context "identity exist" do
      let(:identity) { build(:identity, user: user) }

      it "return user" do
        allow(Identity).to receive(:find_by).with(provider: auth.provider, uid: auth.uid).and_return(identity)
        expect(Identity).not_to receive(:create)
        described_class.from_omniauth(auth)
      end
    end
  end
end
