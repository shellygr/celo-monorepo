/* tslint:disable no-console */
import {
  coerceMnemonicAccountType,
  generatePrivateKey,
  MNEMONIC_ACCOUNT_TYPE_CHOICES,
  privateKeyToPublicKey,
} from 'src/lib/generate_utils'
import * as yargs from 'yargs'

interface Bip32Argv {
  mnemonic: string
  accountType: string
  index: number
}

export const command = 'public-key'

export const describe = 'command for generating the public key using the bip32 standard'

export const builder = (argv: yargs.Argv) => {
  return argv
    .option('mnemonic', {
      type: 'string',
      description: 'BIP-39 mnemonic',
      demandOption: 'Please specify a mnemonic from which to derive a public key',
      alias: 'm',
    })
    .option('accountType', {
      alias: 'a',
      type: 'string',
      choices: MNEMONIC_ACCOUNT_TYPE_CHOICES,
      required: true,
    })
    .option('index', {
      type: 'number',
      description: 'Index of key to generate',
      demandOption: 'Please specify a key index',
      alias: 'i',
    })
}

/*
 * Given a BIP-39 mnemonic, we generate a level 2 child public key from the private key using the
 * BIP-32 standard.
 * https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
 * https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
 */
export const handler = async (argv: Bip32Argv) => {
  console.log(
    privateKeyToPublicKey(
      generatePrivateKey(argv.mnemonic, coerceMnemonicAccountType(argv.accountType), argv.index)
    )
  )
}
